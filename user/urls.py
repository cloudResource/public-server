"""user URL Configuration

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
    url(r'^v1/register$', views.register),  # 用户注册
    url(r'^v1/login$', views.enter),  # 用户登录
    url(r'^v1/logout$', views.logout),  # 用户退出
    url(r'^v1/info$', views.info),  # 个人中心
    url(r'^v1/sms_codes$', views.sms_codes),  # 获取短信验证码
    url(r'^v1/change_password$', views.change_password),  # 修改密码
    url(r'^v1/forget_password$', views.forget_password),  # 忘记密码
    url(r'^v1/add_label$', views.add_label),  # 添加用户标签
    url(r'^v1/del_label$', views.del_label),  # 删除用户标签
    url(r'^v1/rename$', views.rename),  # 修改用户名
    url(r'^v1/get_teacher$', views.get_teacher),  # 查看全部教师
    url(r'^v1/get_teacher/(?P<uuid>[\w-]+)/data$', views.get_teacher_data),  # 获取教师信息
    url(r'^v1/attention_teacher$', views.AttentionTeachers.as_view()), # POST: 关注教师增删改查 GET: 查看关注的教师
    url(r'^v1/attention_teacher/(?P<uuid>[\w-]+)/$', views.UnfollowTeachers.as_view()), # DELETE: 取消关注教师
]
