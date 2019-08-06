"""manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^get_teachers$', views.get_teachers),  # 查询所有教师
    url(r'^add_teacher$', views.add_teacher),  # 添加教师
    url(r'^del_teacher$', views.del_teacher),  # 删除教师
    url(r'^get_classes$', views.get_classes),  # 查询所有班级
    url(r'^add_grade$', views.add_grade),  # 添加年级
    url(r'^add_class$', views.add_class),  # 添加班级
    url(r'^get_projects$', views.get_projects),  # 查询项目信息
    url(r'^login$', views.login),  # 学校管理员登录
    url(r'^logout$', views.logout),  # 学校管理员退出
]
