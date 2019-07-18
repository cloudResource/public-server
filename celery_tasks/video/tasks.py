import os
from ctypes import cdll
from os import path

import requests

from celery_tasks.main import celery_app

# 装饰器将send_sms_code装饰为异步任务,并设置别名
from video.models import Video, Note, Moment


@celery_app.task(name='save_video')
def save_video(video_name):
    """
    保存SD卡中的视频到本地
    :video_name: 视频名称
    :return:
    """
    try:
        url = "http://192.168.2.235" + "/DCIM/Video/" + video_name
        video_path = "/dev/shm/videos/" + video_name + "/"
        folder = os.path.exists(video_path)
        if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(video_path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        req = requests.get(url)
        if req.status_code == 404:
            return False
        # 这里使用文件对象打开文件，使用二进制写入方法打开文件，如果文件不存在会创建文件
        with open(video_path + video_name, 'wb') as fobj:
            # 直接把requests的内容也就是content以二进制方式写入文件，下载完成
            fobj.write(req.content)

        portion = os.path.splitext(video_path + video_name)  # 分离文件名与扩展名
        d = os.path.dirname(__file__)
        cur = cdll.LoadLibrary(d + '/videocv.so')
        get_video = cur.Video
        if portion[1] != '.MP4':
            newname = portion[0] + '.MP4'
            os.rename(video_path + video_name, newname)
            new_video = newname.split("/")[-1]
            os.system('ffmpeg -i %s -vcodec h264 -acodec aac %s' % (newname, video_path + "h264_" + new_video))
            get_video((video_path + "h264_" + new_video).encode())
        else:
            os.system('ffmpeg -i %s -vcodec h264 -acodec aac %s' % (video_path + video_name, video_path + "h264_" + video_name))
            get_video((video_path + "h264_" + video_name).encode())
        videos_obj = Video.objects.get(name=video_name)
        # size = os.path.getsize(video_path)
        videos_obj.status = True
        videos_obj.image_path = video_path + "cover.png"
        videos_obj.save()
        note_list = os.listdir(video_path + "blackboard")
        for i in note_list:
            note_time, suffix = os.path.splitext(i)
            note_obj = Note.objects.create(note_path=video_path + "blackboard/" + i, video_id=videos_obj, note_time=note_time)
            note_obj.save()
        moment_list = os.listdir(video_path + "playback")
        for i in moment_list:
            moment_time, suffix = os.path.splitext(i)
            moment_obj = Moment.objects.create(moment_path=video_path + "playback/" + i, video_id=videos_obj, moment_time=moment_time)
            moment_obj.save()
        return True
    except Exception as e:
        return False
