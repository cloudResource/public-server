import re

from django.http import JsonResponse, HttpResponse
import xlrd
import pandas
from django.utils.http import urlquote

from manager.models import Teacher, Class, Project
from user.models import User
import logging
# Create your views here.

from utils.decoration import check_login

logger = logging.getLogger("django")


@check_login()
def get_teachers(request):
    """
    查询所有教师

    """
    admin_user_id = request.session.get('user_id')
    try:
        school_obj = User.objects.filter(id=admin_user_id).first().school
        teacher_set = Teacher.objects.filter(school_id=school_obj)
        data = {"data": []}
        for teacher_obj in teacher_set:
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.user_id.username
            teacher_mobile = teacher_obj.user_id.mobile
            teacher_dict = {"teacher_id": teacher_id, "teacher_name": teacher_name, "teacher_mobile": teacher_mobile}
            data["data"].append(teacher_dict)
        data["status"] = 200
        return JsonResponse(data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)


@check_login()
def add_teacher(request):
    """
    添加教师

    """
    teacher_name = request.POST.get('teacher_name')
    mobile = request.POST.get('mobile')
    admin_user_id = request.session.get('user_id')
    if not all([teacher_name, mobile]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        school_obj = User.objects.filter(id=admin_user_id).first().school
        user_obj = User.objects.filter(mobile=mobile).first()
        if not user_obj:
            return JsonResponse(data={"error": "该账号未注册", "status": 400})
        teacher = Teacher.objects.filter(user_id=user_obj).first()
        if teacher:
            return JsonResponse(data={"error": "请勿重复添加", "status": 400})
        user_obj.username = teacher_name
        user_obj.role = "teacher"
        user_obj.save()
        teacher_obj = Teacher.objects.create(school_id=school_obj, user_id=user_obj)
        return JsonResponse(data={"data": {"teacher_id": teacher_obj.id,
                                           "teacher_name": user_obj.username,
                                           "teacher_mobile": user_obj.mobile},
                                  "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)


@check_login()
def del_teacher(request):
    """
    删除教师

    """
    teacher_id = request.POST.get('teacher_id')
    admin_user_id = request.session.get('user_id')
    if not teacher_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        admin_school_obj = User.objects.filter(id=admin_user_id).first().school
        teacher_school_obj = Teacher.objects.filter(id=teacher_id).first().school_id
        if admin_school_obj != teacher_school_obj:
            return JsonResponse(data={"error": "无此权限", "status": 400})
        teacher_obj = Teacher.objects.filter(id=teacher_id).first()
        if not teacher_obj:
            return JsonResponse(data={"error": "此教师不存在或已删除", "status": 400})
        teacher_obj.delete()
        return JsonResponse(data={"message": "删除成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "删除失败", "status": 400}, status=400)


@check_login()
def del_class(request):
    """
    删除班级

    """
    class_id = request.POST.get('class_id')
    admin_user_id = request.session.get('user_id')
    if not class_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        admin_school_obj = User.objects.filter(id=admin_user_id).first().school
        class_obj = Class.objects.filter(id=class_id).first()
        if not class_obj:
            return JsonResponse(data={"error": "此教室不存在或已删除", "status": 400})
        class_school_obj = class_obj.school_id
        if admin_school_obj != class_school_obj:
            return JsonResponse(data={"error": "无此权限", "status": 400})
        class_obj.delete()
        return JsonResponse(data={"message": "删除成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "删除失败", "status": 400}, status=400)


@check_login()
def get_classes(request):
    """
    查询所有班级

    """
    admin_user_id = request.session.get('user_id')
    data = {"data": []}
    try:
        admin_school_obj = User.objects.filter(id=admin_user_id).first().school
        class_set = Class.objects.filter(school_id=admin_school_obj)
        for class_obj in class_set:
            class_dict = dict()
            class_dict["class_id"] = class_obj.id
            class_dict["class_name"] = class_obj.class_name
            class_dict["grade_name"] = class_obj.grade_name
            data["data"].append(class_dict)
        data["status"] = 200
        return JsonResponse(data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400}, status=400)


@check_login()
def add_class(request):
    """
    添加教室

    """
    class_name = request.POST.get('class_name')
    grade_name = request.POST.get('grade_name')
    admin_user_id = request.session.get('user_id')
    if not all([class_name, grade_name]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        admin_school_obj = User.objects.filter(id=admin_user_id).first().school
        Class.objects.create(school_id=admin_school_obj, class_name=class_name, grade_name=grade_name)
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400}, status=400)


@check_login()
def file_down(request):
    """
    下载excel模板
    :param request:
    :return:
    """
    file_type = request.GET.get('file_type')
    if not file_type:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})

    if file_type == "teacher_excel":
        with open('/opt/excel_template/批量添加教师模板.xlsx', 'rb') as model_excel:
            result = model_excel.read()
        response = HttpResponse(result)
        title = '批量添加教师模板.xlsx'
        response['Content-Disposition'] = 'attachment; filename="%s"' % (urlquote(title))
        return response
    elif file_type == "class_excel":
        with open('/opt/excel_template/批量添加教室模板.xlsx', 'rb') as model_excel:
            result = model_excel.read()
        response = HttpResponse(result)
        title = '批量添加教室模板.xlsx'
        response['Content-Disposition'] = 'attachment; filename="%s"' % (urlquote(title))
        return response
    else:
        return JsonResponse(data={"error": "模板类型错误", "status": 400})


@check_login()
def batch_add_teacher(request):
    """
    批量添加教师
    :param request:
    :return:
    """
    excel_file = request.FILES.get("excel_file", None)  # 文件对象
    admin_user_id = request.session.get('user_id')
    try:
        admin_school_obj = User.objects.filter(id=admin_user_id).first().school
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())  # xlsx文件
        table = data.sheets()[0]
        for i in range(1, table.nrows):  # table.nrows 是文件行数，第0行是字段名，，，所以有效数据从第1行开始
            print(table.row_values(i))  # table.row_values(i) 就是一行行数据 ，是列表形式
            one_list = []
            for j in range(table.ncols):
                cell_value = table.row_values(i)[j]
                if type(cell_value) is float:
                    cell_value = str(int(cell_value))
                one_list.append(cell_value)
            teacher_name = one_list[0]
            teacher_mobile = one_list[1]
            user_obj = User.objects.filter(mobile=teacher_mobile).first()
            if not user_obj:
                return JsonResponse(data={"error": "账号%s未注册" % teacher_mobile, "status": 400})
            user_obj.username = teacher_name
            user_obj.role = "teacher"
            user_obj.save()
            teacher_obj = Teacher.objects.filter(user_id=user_obj).first()
            if teacher_obj:
                continue
            Teacher.objects.create(school_id=admin_school_obj, user_id=user_obj)
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400}, status=400)


@check_login()
def batch_add_class(request):
    """
    批量添加班级
    :param request:
    :return:
    """
    excel_file = request.FILES.get("excel_file", None)  # 文件对象
    admin_user_id = request.session.get('user_id')
    try:
        admin_school_obj = User.objects.filter(id=admin_user_id).first().school
        data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())  # xlsx文件
        table = data.sheets()[0]
        for i in range(1, table.nrows):  # table.nrows 是文件行数，第0行是字段名，，，所以有效数据从第1行开始
            print(table.row_values(i))  # table.row_values(i) 就是一行行数据 ，是列表形式
            one_list = []
            for j in range(table.ncols):
                cell_value = table.row_values(i)[j]
                if type(cell_value) is float:
                    cell_value = str(int(cell_value))
                one_list.append(cell_value)
            grade_name = one_list[0]
            class_name = one_list[1]
            class_obj = Class.objects.filter(grade_name=grade_name, class_name=class_name).first()
            if class_obj:
                continue
            Class.objects.create(grade_name=grade_name, class_name=class_name, school_id=admin_school_obj)
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400}, status=400)


def get_projects(request):
    """
    获取项目相关信息

    """
    try:
        project_set = Project.objects.all()
        project_list = []
        for project_obj in project_set:
            project_id = project_obj.id
            project_name = project_obj.name
            app_id = project_obj.app_id
            app_secret = project_obj.app_secret
            project_dict = {"project_id": project_id,
                            "project_name": project_name,
                            "app_id": app_id,
                            "app_secret": app_secret}
            project_list.append(project_dict)
        return JsonResponse(data={"data": project_list, "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)


def login(request):
    """
    实现学校管理员登录

    """
    mobile = request.POST.get('mobile')
    password = request.POST.get('password')
    # remembered = request.POST.get('remembered')
    # 校验参数
    if not all([mobile, password]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', mobile):
        return JsonResponse(data={"error": "请输入正确的手机号", "status": 400})
    try:
        # 使用手机号查询用户是否存在，如果用户存在，再校验密码是否正确
        user = User.objects.filter(mobile=mobile).first()
        if not user:
            return JsonResponse(data={"error": "账号不存在", "status": 400})
        if user.password != password:
            return JsonResponse(data={"error": "密码错误", "status": 400})
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
        return JsonResponse(
            data={"data": {"user_name": user_name,
                           "role": role,
                           "mobile": mobile},
                  "status": 200},
            status=200)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "登录失败", "status": 400}, status=400)


def logout(request):
    """
    实现学校管理员退出

    """
    request.session.flush()
    return JsonResponse(data={"message": "退出成功", "status": 200})
