"""yysb URL Configuration

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
    url(r'^register$', views.register), # 用户注册
    url(r'^login$', views.enter), # 用户登录
    url(r'^logout$', views.logout), # 用户登录
    url(r'^info$', views.info), # 个人中心
    url(r'^sms_codes$', views.sms_codes), # 获取短信验证码
    url(r'^change_password$', views.change_password), # 修改密码
    url(r'^forget_password$', views.forget_password), # 忘记密码
    url(r'^add_label$', views.add_label), # 添加用户标签
]
