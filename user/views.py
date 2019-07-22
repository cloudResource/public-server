import random
import re

from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.shortcuts import render
import logging

# Create your views here.
from django_redis import get_redis_connection
from pymysql import DatabaseError

from celery_tasks.sms.yuntongxun.sms import CCP
from user import constants
from celery_tasks.sms.tasks import send_sms_code
from user.models import User, Label

logger = logging.getLogger("django.request")


def enter(request):
    """实现用户登录逻辑"""
    # 接收参数
    try:
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
        except:
            return JsonResponse(data={"error": "账号或密码错误", "status": 400})
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
        return JsonResponse(data={"error": "登录失败", "status": 400})


def logout(request):
    """实现用户退出"""
    request.session.flush()
    return JsonResponse(data={"message": "退出成功", "status": 200})


def add_label(request):
    """添加用户标签"""
    try:
        label = request.POST.get('label')
        user_id = request.session.get('user_id')
        # 校验参数
        if not label:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        labels = Label.objects.filter(user_id=user_id)
        count = len(labels)
        if count >= 3:
            return JsonResponse(data={"error": "只能添加三个标签", "status": 400})
        user_obj = User.objects.get(id=user_id)
        Label.objects.create(label=label, user_id=user_obj)
        return JsonResponse(data={"message": "添加用户标签成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加用户标签失败", "status": 400})


def info(request):
    """个人中心"""
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse(data={"error": "登录过期", "status": 401})
        user = User.objects.get(id=user_id)
        label_set = user.label_set.all()
        label_list = []
        for label_obj in label_set:
            label_list.append(label_obj.label)
        mobile = user.mobile
        user_name = user.username
        role = user.role
        data = {"mobile": mobile, "user_name": user_name, "role": role, "label": label_list}
        return JsonResponse(data={"data": data, "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


def change_password(request):
    """修改密码"""
    try:
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
        except:
            return JsonResponse(data={"error": "修改密码失败", "status": 400})
        # 清理状态保持信息
        request.session.flush()
        return JsonResponse(data={"message": "修改密码成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "修改密码失败", "status": 400})


def forget_password(request):
    """忘记密码"""
    try:
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
        user = User.objects.get(mobile=mobile)
        user.password = password
        user.save()
        return JsonResponse(data={"message": "修改密码成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        if e == "User matching query does not exist.":
            return JsonResponse(data={"error": "此手机号未注册", "status": 400})
        return JsonResponse(data={"error": "修改密码失败", "status": 400})


def register(request):
    """实现用户注册"""
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        # allow = request.POST.get('allow')
        if not all([username, mobile, password, password2]):
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return JsonResponse(data={"error": "请输入8-20位的密码", "status": 400})
        # 判断用户名是否是5-20个字符
        # if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
        #     return JsonResponse(data={"error": "请输入5-20个字符的用户名", "status": 400})
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
        # 判断是否勾选用户协议
        # if allow != 'on':
        #     return JsonResponse(data={"message": "请勾选用户协议", "status": 400})
        User.objects.create(username=username, mobile=mobile, password=password, )
        return JsonResponse(data={"message": "注册成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        pat = r"Duplicate entry.*for key 'mobile'"
        result = re.findall(pat, e)
        if result:
            return JsonResponse(data={"error": "手机号已注册", "status": 400})
        return JsonResponse(data={"error": "注册失败", "status": 400})


def sms_codes(request):
    """
    发送短信验证码
    :param request:
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
