from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


def add_teacher(request):
    """添加教师"""
    role = request.session.get('role')
    if role != "学校管理员":
        return JsonResponse(data={"message": "您无权操作", "status": 400})