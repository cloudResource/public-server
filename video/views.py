from os import path

from django.http import JsonResponse, FileResponse, request, StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from celery_tasks.video.tasks import save_video
# Create your views here.
from video.control import *
import logging
import os
import re
import mimetypes
from wsgiref.util import FileWrapper

from video.models import Video, Note, Moment

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


def list_video(request):
    """
    查看所有视频信息
    :param requests:
    :return:
    """
    data = {"data": []}
    try:
        videos_obj = Video.objects.all()
        for video in videos_obj:
            video_dict = {}
            note_list = []
            moment_list = []
            notes_obj = video.note_set.all()
            moment_obj = video.moment_set.all()
            for note in notes_obj:
                note_list.append({"note_id": note.id, "note_time": note.note_time})
            for moment in moment_obj:
                moment_list.append({"moment_id": moment.id, "moment_time": moment.moment_time})
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


def video_address(request):
    """
    视频播放地址
    :param request:
    :return:
    """
    try:
        video_id = request.GET.get('video_id')
        video_obj = Video.objects.get(id=video_id)
        video_name = video_obj.name
        portion = os.path.splitext(video_name)
        # 如果后缀是jpg
        if portion[1] != '.MP4':
            newname = portion[0] + '.MP4'
            path = '/dev/shm/videos/' + video_name + "/" + "h264_" + newname
        else:
            path = '/dev/shm/videos/' + video_name + "/" + "h264_" + video_name
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_re.match(range_header)
        size = os.path.getsize(path)
        content_type, encoding = mimetypes.guess_type(path)
        content_type = content_type or 'application/octet-stream'
        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = int(last_byte) if last_byte else size - 1
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length),
                                         status=206, content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        else:
            resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
            resp['Accept-Ranges'] = 'bytes'
        return resp
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
    :param request:
    :return:
    """

    video_obj = Video.objects.all()
    pass


def cover_image(request):
    """
    获取封面图片
    :param request:
    :return:
    """
    try:
        video_id = request.GET.get('video_id')
        video_obj = Video.objects.get(id=video_id)
        video_path = video_obj.image_path
        imagepath = path.join(video_path)
        print("imagepath=" + str(imagepath))
        image_data = open(imagepath, "rb").read()
        return HttpResponse(image_data, content_type="image/png")
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "获取图片失败", "status": 400})


def note_image(request):
    """
    获取版书图片
    :param request:
    :return:
    """
    try:
        note_id = request.GET.get('note_id')
        note_obj = Note.objects.get(id=note_id)
        note_path = note_obj.note_path
        imagepath = path.join(note_path)
        print("imagepath=" + str(imagepath))
        image_data = open(imagepath, "rb").read()
        return HttpResponse(image_data, content_type="image/png")
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "获取图片失败", "status": 400})


def moment_image(request):
    """
    获取重点回看图片
    :param request:
    :return:
    """
    try:
        moment_id = request.GET.get('moment_id')
        moment_obj = Moment.objects.get(id=moment_id)
        moment_path = moment_obj.moment_path
        imagepath = path.join(moment_path)
        print("imagepath=" + str(imagepath))
        image_data = open(imagepath, "rb").read()
        return HttpResponse(image_data, content_type="image/png")
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"message": "获取图片失败", "status": 400})
