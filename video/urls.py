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
    url(r'^v1/video_list$', views.video_list),  # 列表查询所有视频
    url(r'^v1/(?P<uuid>[\w-]+)/video_list$', views.teacher_video_list),  # 查询某个教师的所有视频
    url(r'^v1/(?P<uuid>[\w-]+)/video_details$', views.video_details),  # 查询视频详情
    url(r'^v1/(?P<uuid>[\w-]+)/video_share$', views.video_share),  # 查询分享的视频信息，无token验证
    url(r'^v1/comment$', views.CommentListCreateView.as_view()),  # POST: 给某个视频添加一条评论 GET: 获取某个视频所有评论
    url(r'^v1/comment/(?P<uuid>[\w-]+)/$', views.CommentDeleteView.as_view()),  # DELETE: 删除某条评论
    url(r'^v1/attention_videos$', views.attention_videos),  # 获取关注教师的视频(所有教师的视频)
    url(r'^v1/change/video_name$', views.change_video_name),  # 更改视频名称
    url(r'^v1/own_videos$', views.own_videos),  # 教师获取自己的视频
    url(r'^v1/moment$', views.MomentCreateView.as_view()),  # POST: 教师设置精彩时刻
    url(r'^v1/moment/(?P<uuid>[\w-]+)/$', views.MomentDeleteView.as_view()),  # DELETE: 教师删除精彩时刻
    url(r'^v1/video_start$', views.video_start),  # 开始录制视频
    url(r'^v1/video_stop$', views.video_stop),  # 结束录制视频
    url(r'^v1/video_issue$', views.video_issue),  # 发布视频
    url(r'^v1/video_delete$', views.video_delete),  # 发布视频
    url(r'^v1/get_classes$', views.get_classes),  # 小程序获取所有教室
    url(r'^v1/blackboard/is_hide$', views.is_hide_blackboard),  # 教师设置是否隐藏版书
]
