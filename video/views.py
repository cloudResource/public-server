from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView

from celery_tasks.video.tasks import save_video
# Create your views here.
from manager.models import RelationUser
from user.models import User
from utils.decoration import check_token, drf_check_token
from video.control import *
import logging
from video.models import Video, Moment, Comment

logger = logging.getLogger("django")


def start_recording(request):
    """
    开始录制视频
    :param request:
    :return:
    """
    try:
        # 切换摄像头状态
        change_ret = switch_state(1)
        if change_ret is False:
            return JsonResponse(data={"error": "摄像头切换录制模式错误，请检查您的网络", "status": 400})
        # 结束当前视频
        stop_ret = video_recording(0)
        if stop_ret is False:
            return JsonResponse(data={"error": "连接摄像头时发生错误，请检查您的网络", "status": 400})
        # 删除设备SD卡内所有文件
        delete_ret = del_all_files()
        if delete_ret is False:
            return JsonResponse(data={"error": "连接设备SD卡时发生错误，请检查您的网络", "status": 400})
        # 开始录制视频
        start_ret = video_recording(1)
        if start_ret is False:
            return JsonResponse(data={"error": "录制视频错误，请检查您的网络", "status": 400})
        return JsonResponse(data={"message": "开始录制成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "开始录制失败", "status": 400})


def stop_recording(request):
    """
    结束录制视频
    :param request:
    :return:
    """
    try:
        # 结束当前视频
        stop_ret = video_recording(0)
        if stop_ret is False:
            return JsonResponse(data={"error": "连接摄像头时发生错误，请检查您的网络", "status": 400})
        # 获取所有视频文件
        video_ret = get_files()
        if video_ret is False:
            return JsonResponse(data={"error": "连接设备SD卡时发生错误，请检查您的网络", "status": 400})
        for video in video_ret:
            timestamp = unix_time(video["time"])
            try:
                video_obj = Video.objects.create(name=video["name"], end_time=timestamp, size=video["size"])
                video_obj.save()
            except Exception as e:
                logger.error(e)
                return JsonResponse(data={"error": "结束录制失败", "status": 400})
            # 保存SD卡中的视频到本地
            save_video.delay(video["name"])
        return JsonResponse(data={"message": "结束录制成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "结束录制失败", "status": 400})


@check_token()
def list_video(request, token, *args, **kwargs):
    """
    查看所有视频信息
    :param request:
    :return:
    """
    data = {"data": []}
    try:
        user = User.objects.filter(openid=token).first()
        if not user:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        videos_obj = Video.objects.all()
        for video in videos_obj:
            video_dict = dict()
            note_list = list()
            moment_list = list()
            label_list = list()
            notes_set = video.note_set.all()
            moment_set = video.moment_set.all()
            label_set = video.teacher_id.user_id.label_set.all()
            for label_obj in label_set:
                label_list.append({"label": label_obj.label})
            for note_obj in notes_set:
                note_list.append({"note_id": note_obj.id,
                                  "note_time": note_obj.note_time,
                                  "note_path": note_obj.note_path})
            for moment_obj in moment_set:
                moment_list.append(
                    {"moment_id": moment_obj.id,
                     "moment_time": moment_obj.moment_time,
                     "start_time": moment_obj.start_time,
                     "stop_time": moment_obj.stop_time,
                     "moment_path": moment_obj.moment_path})
            teacher_obj = video.teacher_id
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.user_id.username
            teacher_school = teacher_obj.school_id.school_name
            relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user).first()
            if relation_user_obj:
                is_attention = True
            else:
                is_attention = False
            teacher_dict = {"teacher_id": teacher_id,
                            "teacher_name": teacher_name,
                            "teacher_school": teacher_school,
                            "is_attention": is_attention}
            video_dict["video_id"] = video.id
            video_dict["video_name"] = video.video_name
            video_dict["file_path"] = video.file_path
            video_dict["teacher_data"] = teacher_dict
            video_dict["end_time"] = video.end_time
            video_dict["image_path"] = video.image_path
            video_dict["video_status"] = video.status
            video_dict["domain"] = video.teacher_id.school_id.domain
            video_dict["video_notes"] = note_list
            video_dict["video_moments"] = moment_list
            video_dict["label_list"] = label_list
            data["data"].append(video_dict)
        data["status"] = 200
        return JsonResponse(data=data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


class ReviewData(ListCreateAPIView):
    """
    METHOD: 请求方法
        get: 给某个视频添加一条评论
        post: 获取某个视频所有评论
    """

    @drf_check_token()
    def get(self, request, *args, **kwargs):
        """
        获取某个视频所有评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        uuid = int(kwargs.get("uuid"))
        if not uuid:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            video_obj = Video.objects.filter(id=uuid).first()
            if not video_obj:
                return JsonResponse(data={"error": "该视频不存在", "status": 400})
            comment_set = Comment.objects.filter(video_id=video_obj)
            comment_list = list()
            for comment_obj in comment_set:
                comment_dict = dict()
                user_dict = dict()
                comment_id = comment_obj.id
                comment_data = comment_obj.comment
                user_id = comment_obj.user_id.id
                user_name = comment_obj.user_id.username
                label_set = comment_obj.user_id.label_set.all()
                label_list = list()
                for label_obj in label_set:
                    label_dict = dict()
                    label_dict["id"] = label_obj.id
                    label_dict["label"] = label_obj.label
                    label_list.append(label_dict)
                user_dict["user_id"] = user_id
                user_dict["user_name"] = user_name
                user_dict["label_list"] = label_list
                comment_dict["comment_id"] = comment_id
                comment_dict["comment_data"] = comment_data
                comment_dict["user_dict"] = user_dict
                comment_list.append(comment_dict)
            return JsonResponse(data={"data": comment_list, "status": 200})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "获取数据失败", "status": 400}, status=400)

    @drf_check_token()
    def post(self, request, *args, **kwargs):
        """
        给某个视频添加一条评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        uuid = int(kwargs.get("uuid"))
        comment = request.POST.get('comment')
        if not uuid:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            video_obj = Video.objects.filter(id=uuid).first()
            if not video_obj:
                return JsonResponse(data={"error": "该视频不存在", "status": 400})
            comment_obj = Comment.objects.create(comment=comment, video_id=video_obj, user_id=user_obj)
            comment_dict = dict()
            user_dict = dict()
            comment_id = comment_obj.id
            comment_data = comment_obj.comment
            user_id = comment_obj.user_id.id
            user_name = comment_obj.user_id.username
            label_set = comment_obj.user_id.label_set.all()
            label_list = list()
            for label_obj in label_set:
                label_dict = dict()
                label_dict["id"] = label_obj.id
                label_dict["label"] = label_obj.label
                label_list.append(label_dict)
            user_dict["user_id"] = user_id
            user_dict["user_name"] = user_name
            user_dict["label_list"] = label_list
            comment_dict["comment_id"] = comment_id
            comment_dict["comment_data"] = comment_data
            comment_dict["user_dict"] = user_dict
            return JsonResponse(data={"data": comment_dict, "status": 200})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "发布评论失败", "status": 400}, status=400)


class ReviewDataDel(ListCreateAPIView):
    """
    METHOD: 请求方法
        delete: 删除某条评论
    """

    @drf_check_token()
    def delete(self, request, *args, **kwargs):
        """
        删除某条评论
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        uuid = int(kwargs.get("uuid"))
        if not uuid:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            comment_obj = Comment.objects.filter(id=uuid).first()
            if not comment_obj:
                return JsonResponse(data={"error": "该评论不存在", "status": 400})
            if comment_obj.user_id.openid != token:
                return JsonResponse(data={"error": "无权操作", "status": 400})
            comment_obj.delete()
            return JsonResponse(data={"data": {"message": "删除评论成功", "status": 200}})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "删除评论失败", "status": 400}, status=400)


@check_token()
def change_video_name(request, token, *args, **kwargs):
    """
    更改视频名字
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    video_name = request.POST.get('video_name')
    video_id = request.POST.get('video_id')
    if not all([video_name, video_id]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "视频不存在", "status": 400})
        openid = video_obj.teacher_id.user_id.openid
        if openid != token:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        video_obj.video_name = video_name
        video_obj.save()
        return JsonResponse(data={"message": "保存成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加用户标签失败", "status": 400}, status=400)


@check_token()
def attention_videos(request, token, *args, **kwargs):
    """
    获取关注教师的视频
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    data = {"data": []}
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        teacher_set = RelationUser.objects.filter(user_id=user_obj)
        for teacher_obj in teacher_set:
            video_set = Video.objects.filter(teacher_id=teacher_obj.teacher_id)
            for video_obj in video_set:
                video_dict = dict()
                note_list = list()
                moment_list = list()
                label_list = list()
                notes_set = video_obj.note_set.all()
                moment_set = video_obj.moment_set.all()
                label_set = video_obj.teacher_id.user_id.label_set.all()
                for label_obj in label_set:
                    label_list.append({"label": label_obj.label})
                for note_obj in notes_set:
                    note_list.append({"note_id": note_obj.id,
                                      "note_time": note_obj.note_time,
                                      "note_path": note_obj.note_path})
                for moment_obj in moment_set:
                    moment_list.append(
                        {"moment_id": moment_obj.id,
                         "moment_time": moment_obj.moment_time,
                         "moment_path": moment_obj.moment_path})
                teacher_obj = video_obj.teacher_id
                teacher_id = teacher_obj.id
                teacher_name = teacher_obj.user_id.username
                teacher_school = teacher_obj.school_id.school_name
                teacher_dict = {"teacher_id": teacher_id,
                                "teacher_name": teacher_name,
                                "teacher_school": teacher_school}
                video_dict["video_id"] = video_obj.id
                video_dict["video_name"] = video_obj.video_name
                video_dict["file_path"] = video_obj.file_path
                video_dict["teacher_data"] = teacher_dict
                video_dict["end_time"] = video_obj.end_time
                video_dict["image_path"] = video_obj.image_path
                video_dict["video_status"] = video_obj.status
                video_dict["domain"] = video_obj.teacher_id.school_id.domain
                video_dict["video_notes"] = note_list
                video_dict["video_moments"] = moment_list
                video_dict["label_list"] = label_list
                data["data"].append(video_dict)
        data["status"] = 200
        return JsonResponse(data=data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


@check_token()
def own_videos(request, token, *args, **kwargs):
    """
    获取自己的视频（教师）
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    data = {"data": []}
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role != "teacher":
            return JsonResponse(data={"error": "角色不匹配，无权查看", "status": 400})
        video_set = user_obj.teacher.video_set.all()
        for video_obj in video_set:
            video_dict = dict()
            note_list = list()
            moment_list = list()
            label_list = list()
            notes_set = video_obj.note_set.all()
            moment_set = video_obj.moment_set.all()
            label_set = video_obj.teacher_id.user_id.label_set.all()
            for label_obj in label_set:
                label_list.append({"label": label_obj.label})
            for note_obj in notes_set:
                note_list.append({"note_id": note_obj.id,
                                  "note_time": note_obj.note_time,
                                  "note_path": note_obj.note_path})
            for moment_obj in moment_set:
                moment_list.append(
                    {"moment_id": moment_obj.id,
                     "moment_time": moment_obj.moment_time,
                     "start_time": moment_obj.start_time,
                     "stop_time": moment_obj.stop_time,
                     "moment_path": moment_obj.moment_path})
            teacher_obj = video_obj.teacher_id
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.user_id.username
            teacher_school = teacher_obj.school_id.school_name
            relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user_obj).first()
            if relation_user_obj:
                is_attention = True
            else:
                is_attention = False
            teacher_dict = {"teacher_id": teacher_id,
                            "teacher_name": teacher_name,
                            "teacher_school": teacher_school,
                            "is_attention": is_attention}
            video_dict["video_id"] = video_obj.id
            video_dict["video_name"] = video_obj.video_name
            video_dict["file_path"] = video_obj.file_path
            video_dict["teacher_data"] = teacher_dict
            video_dict["end_time"] = video_obj.end_time
            video_dict["image_path"] = video_obj.image_path
            video_dict["video_status"] = video_obj.status
            video_dict["domain"] = video_obj.teacher_id.school_id.domain
            video_dict["video_notes"] = note_list
            video_dict["video_moments"] = moment_list
            video_dict["label_list"] = label_list
            data["data"].append(video_dict)
        data["status"] = 200
        return JsonResponse(data=data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


@check_token()
def set_param_moment(request, token, *args, **kwargs):
    """
    为视频精彩时刻添加参数
    :param request:
    :param token: 用户验证，唯一标识
    :param args:
    :param kwargs:
    :return:
    """
    uuid = int(kwargs.get("uuid"))
    start_time = request.POST.get('start_time')
    stop_time = request.POST.get('stop_time')
    if not all([uuid, start_time, stop_time]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        moment_obj = Moment.objects.filter(id=uuid).first()
        openid = moment_obj.video_id.teacher_id.user_id.openid
        if openid != token:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        moment_obj.start_time = int(start_time)
        moment_obj.stop_time = int(stop_time)
        moment_obj.save()
        return JsonResponse(data={"message": "添加成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "添加失败", "status": 400})
