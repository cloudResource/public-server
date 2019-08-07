import re

from django.http import JsonResponse

from manager.models import Teacher, Grade, Class, Project
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
        school_obj = User.objects.get(id=admin_user_id).school
        teacher_set = Teacher.objects.filter(school_id=school_obj)
        data = {"data": []}
        teacher_list = []
        for teacher_obj in teacher_set:
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.user_id.username
            teacher_mobile = teacher_obj.user_id.mobile
            teacher_dict = {"teacher_id": teacher_id, "teacher_name": teacher_name, "teacher_mobile": teacher_mobile}
            teacher_list.append(teacher_dict)
        data["data"].append(teacher_list)
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
    try:
        school_obj = User.objects.get(id=admin_user_id).school
        user_obj = User.objects.get(mobile=mobile)
        user_obj.username = teacher_name
        user_obj.role = "teacher"
        user_obj.save()
        Teacher.objects.create(school_id=school_obj, user_id=user_obj)
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        if e == "User matching query does not exist.":
            return JsonResponse(data={"error": "此手机号未注册", "status": 400})
        return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)


@check_login()
def del_teacher(request):
    """
    删除教师

    """
    teacher_id = request.POST.get('teacher_id')
    admin_user_id = request.session.get('user_id')
    try:
        admin_school_obj = User.objects.get(id=admin_user_id).school
        teacher_school_obj = Teacher.objects.get(id=teacher_id).school_id
        if admin_school_obj != teacher_school_obj:
            return JsonResponse(data={"error": "无此权限", "status": 400})
        Teacher.objects.get(id=teacher_id).delete()
        return JsonResponse(data={"message": "删除成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        if e == "Teacher matching query does not exist.":
            return JsonResponse(data={"error": "此教师不存在或已删除", "status": 400})
        return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)


@check_login()
def get_classes(request):
    """
    查询所有班级

    """
    admin_user_id = request.session.get('user_id')
    try:
        admin_school_obj = User.objects.get(id=admin_user_id).school
        grade_set = Grade.objects.filter(school_id=admin_school_obj)
        data = {"data": []}
        for grade_obj in grade_set:
            grade_dict = {"grade_id": grade_obj.id, "grade_name": grade_obj.grade_name, "classes": []}
            class_set = Class.objects.filter(grade_id=grade_obj)
            for class_obj in class_set:
                class_dict = dict()
                class_dict["class_id"] = class_obj.id
                class_dict["class_name"] = class_obj.class_name
                grade_dict["classes"].append(class_dict)
            data["data"].append(grade_dict)
            data["status"] = 200
        return JsonResponse(data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400}, status=400)


@check_login()
def add_grade(request):
    """
    添加年级

    """
    admin_user_id = request.session.get('user_id')
    grade_name = request.POST.get('grade_name')
    try:
        admin_school_obj = User.objects.get(id=admin_user_id).school
        Grade.objects.create(school_id=admin_school_obj, grade_name=grade_name)
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400}, status=400)


@check_login()
def add_class(request):
    """
    添加教室

    """
    class_name = request.POST.get('class_name')
    grade_id = request.POST.get('grade_id')
    admin_user_id = request.session.get('user_id')
    try:
        admin_school_obj = User.objects.get(id=admin_user_id).school
        grade_obj = Grade.objects.get(id=grade_id)
        Class.objects.create(school_id=admin_school_obj, class_name=class_name, grade_id=grade_obj)
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
