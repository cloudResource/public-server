import random
import re
from rest_framework.generics import *
from django.http import JsonResponse
import logging

from django_redis import get_redis_connection

from manager.models import Teacher, RelationUser
from user import constants
from celery_tasks.sms.tasks import send_sms_code
from user.models import User, Label
from utils.decoration import check_token, drf_check_token

# Create your views here.

logger = logging.getLogger("django")


def enter(request, *args, **kwargs):
    """
    用户登录
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    mobile = request.POST.get('mobile')
    password = request.POST.get('password')
    # remembered = request.POST.get('remembered')
    # 校验参数
    if not all([mobile, password]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', mobile):
        return JsonResponse(data={"error": "请输入正确的手机号", "status": 400})
    if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
        return JsonResponse(data={"error": "密码最少8位，最长20位", "status": 400})
        # 使用手机号查询用户是否存在，如果用户存在，再校验密码是否正确
    try:
        user = User.objects.get(mobile=mobile)
        if user.password != password:
            return JsonResponse(data={"error": "账号或密码错误", "status": 400})
        role = user.role
        user_name = user.username
        user_id = user.id
        # 状态保持
        request.session['user_id'] = user_id
        request.session['user_name'] = user_name
        request.session['mobile'] = mobile
        request.session['password'] = password
        request.session["role"] = role
        request.session.set_expiry(7200)
        return JsonResponse(data={"data": {"user_name": user_name, "role": role, "mobile": mobile}, "status": 200},
                            status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "登录失败", "status": 404}, status=404)


def logout(request, *args, **kwargs):
    """
    实现用户退出
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    request.session.flush()
    return JsonResponse(data={"message": "退出成功", "status": 200})


@check_token()
def add_label(request, token, *args, **kwargs):
    """
    添加用户标签
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    label = request.POST.get('label')
    # 校验参数
    if not label:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        labels = Label.objects.filter(user_id=user_obj.id)
        count = len(labels)
        if count >= 3:
            return JsonResponse(data={"error": "只能添加三个用户标签", "status": 400})
        Label.objects.create(label=label, user_id=user_obj)
        return JsonResponse(data={"message": "添加用户标签成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加用户标签失败", "status": 400}, status=400)


@check_token()
def del_label(request, token, *args, **kwargs):
    """
    删除用户标签
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    label_id = request.POST.get('label_id')
    # 校验参数
    if not label_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        label_obj = Label.objects.filter(id=label_id).first()
        if not label_obj:
            return JsonResponse(data={"error": "标签不存在", "status": 400})
        openid = label_obj.user_id.openid
        if token != openid:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        Label.objects.filter(id=label_id).delete()
        return JsonResponse(data={"message": "删除用户标签成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "删除用户标签失败", "status": 400}, status=400)


@check_token()
def info(request, token, *args, **kwargs):
    """
    个人中心
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    try:
        user = User.objects.filter(openid=token).first()
        if not user:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        label_set = user.label_set.all()
        label_list = []
        for label_obj in label_set:
            label_dict = dict()
            label_dict["id"] = label_obj.id
            label_dict["label"] = label_obj.label
            label_list.append(label_dict)
        mobile = user.mobile
        user_name = user.username
        role = user.role
        data = {"mobile": mobile, "user_name": user_name, "role": role, "label": label_list}
        return JsonResponse(data={"data": data, "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 404}, status=404)


def change_password(request, *args, **kwargs):
    """
    修改密码
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    old_password = request.POST.get('old_password')
    new_password = request.POST.get('new_password')
    new_password2 = request.POST.get('new_password2')
    password = request.session.get('password')
    user_id = request.session.get('user_id')
    # 校验参数
    if not all([old_password, new_password, new_password2]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    if old_password != password:
        return JsonResponse(data={"error": "原始密码错误", "status": 400})
    if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
        return JsonResponse(data={"error": "密码最少8位，最长20位", "status": 400})
    if new_password != new_password2:
        return JsonResponse(data={"error": "两次输入的密码不一致", "status": 400})
    # 修改密码
    try:
        user = User.objects.get(id=user_id)
        user.password = new_password
        user.save()
        request.session.flush()
        return JsonResponse(data={"message": "修改密码成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "修改密码失败", "status": 400}, status=400)


def forget_password(request, *args, **kwargs):
    """
    忘记密码
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    mobile = request.POST.get('mobile')
    sms_code_client = request.POST.get('sms_code')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    if not all([sms_code_client, mobile, password, password2]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    # 判断密码是否是8-20个数字
    if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
        return JsonResponse(data={"error": "请输入8-20位的密码", "status": 400})
    # 判断两次密码是否一致
    if password != password2:
        return JsonResponse(data={"error": "两次输入的密码不一致", "status": 400})
    # 判断手机号是否合法
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return JsonResponse(data={"error": "请输入正确的手机号码", "status": 400})
    # 判断短信验证码是否输入正确
    redis_conn = get_redis_connection('verify_codes')
    sms_code_server = redis_conn.get('sms_%s' % mobile)
    if sms_code_server is None:
        return JsonResponse(data={"error": "短信验证码已失效", "status": 400})
    if sms_code_client != sms_code_server.decode():
        return JsonResponse(data={"error": "短信验证码有误", "status": 400})
    try:
        user = User.objects.get(mobile=mobile)
        user.password = password
        user.save()
        return JsonResponse(data={"message": "修改密码成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        if e == "User matching query does not exist.":
            return JsonResponse(data={"error": "此手机号未注册", "status": 400})
        return JsonResponse(data={"error": "修改密码失败", "status": 400}, status=400)


def register(request, *args, **kwargs):
    """
    实现用户注册
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    username = request.POST.get('username')
    # password = request.POST.get('password')
    # password2 = request.POST.get('password2')
    mobile = request.POST.get('mobile')
    sms_code_client = request.POST.get('sms_code')
    openid = request.POST.get('openid')
    if not all([username, mobile, openid]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    # 判断密码是否是8-20个数字
    # if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
    #     return JsonResponse(data={"error": "请输入8-20位的密码", "status": 400})
    # 判断用户名是否是1-20个字符
    # if not re.match(r'^[a-zA-Z0-9_-]{1,20}$', username):
    #     return JsonResponse(data={"error": "请输入1-20个字符的用户名", "status": 400})
    # 判断两次密码是否一致
    # if password != password2:
    #     return JsonResponse(data={"error": "两次输入的密码不一致", "status": 400})
    # 判断手机号是否合法
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return JsonResponse(data={"error": "请输入正确的手机号码", "status": 400})
    # 判断短信验证码是否输入正确
    redis_conn = get_redis_connection('verify_codes')
    sms_code_server = redis_conn.get('sms_%s' % mobile)
    if sms_code_server is None:
        return JsonResponse(data={"error": "短信验证码已失效", "status": 400})
    if sms_code_client != sms_code_server.decode():
        return JsonResponse(data={"error": "短信验证码有误", "status": 400})
    try:
        User.objects.create(username=username, mobile=mobile, openid=openid)
        return JsonResponse(data={"message": "注册成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        pat = r"Duplicate entry.*for key 'mobile'"
        result = re.findall(pat, e)
        if result:
            return JsonResponse(data={"error": "手机号已注册", "status": 400})
        return JsonResponse(data={"error": "注册失败", "status": 400}, status=400)


def sms_codes(request, *args, **kwargs):
    """
    发送短信验证码
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    mobile = request.GET.get('mobile')
    redis_conn = get_redis_connection('verify_codes')
    send_flag = redis_conn.get('send_flag_%s' % mobile)
    if send_flag:
        return JsonResponse(data={"error": "发送短信过于频繁", "status": 400})
    if not mobile:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    # 判断手机号是否合法
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return JsonResponse(data={"error": "请输入正确的手机号码", "status": 400})
    # ⽣成短信验证码：⽣成6位数验证码
    sms_code = '%06d' % random.randint(0, 999999)
    # CCP().send_template_sms(mobile,[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
    # celery异步发送短信
    send_sms_code.delay(mobile, sms_code)
    pl = redis_conn.pipeline()
    # 保存短信验证码
    pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    # 执行
    pl.execute()

    return JsonResponse(data={"message": "发送成功", "status": 200})


@check_token()
def rename(request, token, *args, **kwargs):
    """
    修改用户名
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    user_name = request.POST.get('user_name')
    if not user_name:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        user_obj.username = user_name
        user_obj.save()
        return JsonResponse(data={"message": "保存成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "修改用户名失败", "status": 400}, status=400)


@check_token()
def get_teacher_data(request, token, *args, **kwargs):
    """
    获取教师信息
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    uuid = int(kwargs.get("uuid"))
    if not uuid:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        teacher_obj = Teacher.objects.filter(id=uuid).first()
        if not teacher_obj:
            return JsonResponse(data={"error": "该老师不存在", "status": 400})
        data = dict()
        label_list = list()
        video_list = list()
        for label_obj in teacher_obj.user_id.label_set.all():
            label_list.append({"label": label_obj.label})
        for video_obj in teacher_obj.video_set.all():
            video_list.append({"name": video_obj.name,
                               "is_delete": video_obj.is_delete,
                               "status": video_obj.status,
                               "image_path": video_obj.image_path,
                               "end_time": video_obj.end_time})
        data["name"] = teacher_obj.user_id.username
        data["label"] = label_list
        data["video"] = video_list
        return JsonResponse(data={"data": data, "status": 200})

    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取教师信息失败", "status": 400}, status=400)


class AttentionTeachers(ListCreateAPIView):
    """
    method: 请求方法
        GET: 查询关注教师
        POST: 关注教师
    """
    @drf_check_token()
    def get(self, request, *args, **kwargs):
        """
        查看关注教师
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        try:
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            relation_user_set = RelationUser.objects.filter(user_id=user_obj)
            teacher_list = []
            for relation_user_obj in relation_user_set:
                teacher_id = relation_user_obj.teacher_id.id
                user_name = relation_user_obj.teacher_id.user_id.username
                teacher_dict = {"teacher_id": teacher_id, "user_name": user_name}
                teacher_list.append(teacher_dict)
            return JsonResponse(data={"data": {"teacher_list": teacher_list}, "status": 200})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)

    @drf_check_token()
    def post(self, request, *args, **kwargs):
        """
        关注教师
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        teacher_id = request.POST.get('teacher_id')
        if not teacher_id:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            teacher_obj = Teacher.objects.filter(id=teacher_id).first()
            if not teacher_obj:
                return JsonResponse(data={"error": "该老师不存在", "status": 400})
            relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user_obj).first()
            if relation_user_obj:
                return JsonResponse(data={"error": "已关注该教师", "status": 400})
            RelationUser.objects.create(user_id=user_obj, teacher_id=teacher_obj)
            return JsonResponse(data={"message": "关注教师成功", "status": 200})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "关注教师失败", "status": 400}, status=400)


class UnfollowTeachers(DestroyAPIView):
    """
    method: 请求方法
        DELETE: 取消关注教师
    """
    @drf_check_token()
    def delete(self, request, *args, **kwargs):
        """
        取消关注教师
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        uuid = int(kwargs.get("uuid"))
        try:
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            teacher_obj = Teacher.objects.filter(id=uuid).first()
            if not teacher_obj:
                return JsonResponse(data={"error": "该老师不存在", "status": 400})
            relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user_obj).first()
            if not relation_user_obj:
                return JsonResponse(data={"error": "未关注该教师", "status": 400})
            relation_user_obj.delete()
            return JsonResponse(data={"data": {"message": "取消关注成功", "status": 200}})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)
