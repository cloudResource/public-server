"""video URL Configuration

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
    url(r'^v1/list_video$', views.list_video),  # 列表查询所有视频
    url(r'^v1/comment/(?P<uuid>[\w-]+)/$', views.ReviewData.as_view()),  # POST: 给某个视频添加一条评论 GET: 获取某个视频所有评论
    url(r'^v1/comment/(?P<uuid>[\w-]+)/del$', views.ReviewDataDel.as_view()),  # DELETE: 删除某条评论
    url(r'^v1/attention_videos$', views.attention_videos),  # 获取关注教师的视频
    url(r'^v1/change/video_name$', views.change_video_name),  # 获取关注教师的视频
    url(r'^v1/own_videos$', views.own_videos),  # 获取自己的视频
    url(r'^v1/set_param/(?P<uuid>[\w-]+)/moment$', views.set_param_moment),  # 为视频精彩时刻添加参数
    url(r'^v1/video_start$', views.video_start),  # 开始录制视频
    url(r'^v1/video_stop$', views.video_stop),  # 开始录制视频
]
