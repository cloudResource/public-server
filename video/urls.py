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
    url(r'^start$', views.start_recording),  # 开始录制视频
    url(r'^stop$', views.stop_recording),  # 结束录制视频
    url(r'^list_video$', views.list_video),  # 列表查询所有视频
    url(r'^list_comment$', views.list_comment),  # 获取所有评论
    url(r'^add_comment$', views.add_comment),  # 添加一条评论
    url(r'^video_state$', views.video_state),  # 查看视频上传状态
    url(r'^add_video_label$', views.add_video_label),  # 添加视频标签
]
