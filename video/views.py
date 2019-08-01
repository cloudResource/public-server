from os import path

from django.http import JsonResponse, FileResponse, request, StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from celery_tasks.video.tasks import save_video
# Create your views here.
from user.models import User
from utils.decoration import check_token
from video.control import *
import logging
import os
import re
import mimetypes
from wsgiref.util import FileWrapper

from video.models import Video, Note, Moment, VideoLabel

logger = logging.getLogger("django.request")


def start_recording(request):
    """
    开始录制视频
    :param requests:
    :return:
    """
    try:
        # 切换摄像头状态
        change_ret = switch_state(1)
        if change_ret is False:
            return JsonResponse(data={"message": "摄像头切换录制模式错误，请检查您的网络", "status": 400})
        # 结束当前视频
        stop_ret = video_recording(0)
        if stop_ret is False:
            return JsonResponse(data={"message": "连接摄像头时发生错误，请检查您的网络", "status": 400})
        # 删除设备SD卡内所有文件
        delete_ret = del_all_files()
        if delete_ret is False:
            return JsonResponse(data={"message": "连接设备SD卡时发生错误，请检查您的网络", "status": 400})
        # 开始录制视频
        start_ret = video_recording(1)
        if start_ret is False:
            return JsonResponse(data={"message": "录制视频错误，请检查您的网络", "status": 400})
        return JsonResponse(data={"message": "开始录制成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "开始录制失败", "status": 400})


def stop_recording(request):
    """
    结束录制视频
    :param requests:
    :return:
    """
    try:
        # 结束当前视频
        stop_ret = video_recording(0)
        if stop_ret is False:
            return JsonResponse(data={"message": "连接摄像头时发生错误，请检查您的网络", "status": 400})
        # 获取所有视频文件
        video_ret = get_files()
        if video_ret is False:
            return JsonResponse(data={"message": "连接设备SD卡时发生错误，请检查您的网络", "status": 400})
        for video in video_ret:
            timestamp = unix_time(video["time"])
            try:
                video_obj = Video.objects.create(name=video["name"], end_time=timestamp, size=video["size"])
                video_obj.save()
            except Exception as e:
                logger.error(e)
                return JsonResponse(data={"message": "结束录制失败", "status": 400})
            # 保存SD卡中的视频到本地
            save_video.delay(video["name"])
        return JsonResponse(data={"message": "结束录制成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "结束录制失败", "status": 400})


@check_token("list_video")
def list_video(request, token):
    """
    查看所有视频信息

    """
    data = {"data": []}
    try:
        user = User.objects.filter(openid=token).first()
        if not user:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        videos_obj = Video.objects.all()
        for video in videos_obj:
            video_dict = {}
            note_list = []
            moment_list = []
            notes_obj = video.note_set.all()
            moment_obj = video.moment_set.all()
            for note in notes_obj:
                note_list.append({"note_id": note.id, "note_time": note.note_time, "note_path": note.note_path})
            for moment in moment_obj:
                moment_list.append(
                    {"moment_id": moment.id, "moment_time": moment.moment_time, "moment_path": moment.moment_path})
            video_dict["video_id"] = video.id
            video_dict["video_name"] = video.name
            video_dict["end_time"] = video.end_time
            video_dict["image_path"] = video.image_path
            video_dict["video_status"] = video.status
            video_dict["domain"] = video.teacher_id.school_id.domain
            video_dict["video_notes"] = note_list
            video_dict["video_moments"] = moment_list
            data["data"].append(video_dict)
        data["status"] = 200
        return JsonResponse(data=data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "获取数据失败", "status": 400})


def list_comment(request):
    """
    查看所有评论
    :param request:
    :return:
    """
    # data = {"data": []}
    # try:
    #     comments = Comment.objects.all()
    #     for comment in comments:
    #         comment_dict = {}
    #         comment_dict["name"] = comment.name
    #         comment_dict["comment"] = comment.comment
    #         data["data"].append(comment_dict)
    #     data["status"] = 200
    #     return JsonResponse(data=data)
    # except Exception as e:
    #     logger.error(e)
    #     return JsonResponse(data={"message": "获取数据失败", "status": 400})
    pass


def add_comment(request):
    """
    添加一条评论
    :param request:
    :return:
    """
    # try:
    #     name = request.POST.get("name")
    #     comment = request.POST.get("comment")
    #     comment_obj = Comment.objects.create(name=name, end_time=comment)
    #     comment_obj.save()
    # except Exception as e:
    #     logger.error(e)
    #     return JsonResponse(data={"message": "获取数据失败", "status": 400})
    pass


def video_state(request):
    """
    查看视频上传状态

    """

    video_obj = Video.objects.all()
    pass


@check_token("add_video_label")
def add_video_label(request, token):
    """
    添加视频标签

    """
    video_id = request.POST.get('video_id')
    video_label = request.POST.get('video_label')
    if not all([video_id, video_label]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "视频不存在", "status": 400})
        teacher_openid = video_obj.teacher_id.user_id.openid
        if token != teacher_openid:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        video_label_set = VideoLabel.objects.filter(video_id=video_obj.id)
        count = len(video_label_set)
        if count >= 3:
            return JsonResponse(data={"error": "只能添加三个视频标签", "status": 400})
        VideoLabel.objects.create(video_label=video_label, video_id=video_obj)
        return JsonResponse(data={"message": "添加用户标签成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "获取数据失败", "status": 400})


