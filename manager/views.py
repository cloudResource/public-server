from django.http import JsonResponse
from django.shortcuts import render

from manager.models import Teacher
from user.models import User
import logging

# Create your views here.

logger = logging.getLogger("django.request")


def get_teachers(request):
    """
    查询所有教师
    """
    role = request.session.get('role')
    admin_user_id = request.session.get('user_id')
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse(data={"error": "登录过期", "status": 401})
    if role != "admin":
        return JsonResponse(data={"error": "您无权操作", "status": 400})
    try:
        school_obj = User.objects.get(id=admin_user_id).school
        teacher_set = Teacher.objects.filter(school_id=school_obj)
        data = {"data": []}
        teacher_list = []
        for teacher_obj in teacher_set:
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.name
            teacher_mobile = teacher_obj.user_id.mobile
            teacher_dict = {"teacher_id": teacher_id, "teacher_name": teacher_name, "teacher_mobile": teacher_mobile}
            teacher_list.append(teacher_dict)
        data["data"].append(teacher_list)
        data["status"] = 200
        return JsonResponse(data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


def add_teacher(request):
    """
    添加教师
    """
    teacher_name = request.POST.get('teacher_name')
    mobile = request.POST.get('mobile')
    role = request.session.get('role')
    admin_user_id = request.session.get('user_id')
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse(data={"error": "登录过期", "status": 401})
    if role != "admin":
        return JsonResponse(data={"error": "您无权操作", "status": 400})
    try:
        school_obj = User.objects.get(id=admin_user_id).school
        user_obj = User.objects.get(mobile=mobile)
        Teacher.objects.create(school_id=school_obj, name=teacher_name, user_id=user_obj)
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        e = str(e)
        if e == "User matching query does not exist.":
            return JsonResponse(data={"error": "此手机号未注册", "status": 400})
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


def del_teacher(request):
    """
    删除教师
    """
    teacher_id = request.POST.get('teacher_id')
    role = request.session.get('role')
    admin_user_id = request.session.get('user_id')
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse(data={"error": "登录过期", "status": 401})
    if role != "admin":
        return JsonResponse(data={"error": "您无权操作", "status": 400})
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
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


def add_class(request):
    """
    添加教室
    """
    teacher_id = request.POST.get('teacher_id')
    role = request.session.get('role')
    admin_user_id = request.session.get('user_id')
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse(data={"error": "登录过期", "status": 401})
    if role != "admin":
        return JsonResponse(data={"error": "您无权操作", "status": 400})
    pass