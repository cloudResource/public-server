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
    url(r'^video_address$', views.video_address),  # 视频播放地址
    url(r'^cover_image$', views.cover_image),  # 获取封面图片
    url(r'^note_image$', views.note_image),  # 获取版书图片
    url(r'^moment_image$', views.moment_image),  # 获取精彩回看图片
    url(r'^list_comment$', views.list_comment),  # 获取所有评论
    url(r'^add_comment$', views.add_comment),  # 添加一条评论
    url(r'^video_state$', views.video_state),  # 查看视频上传状态
]
