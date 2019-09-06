from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, DestroyAPIView, CreateAPIView

# Create your views here.
from manager.models import *
from public_server.settings import PAGINATOR
from user.models import User
from utils.DataPaginator import data_paginator
from utils.decoration import check_token, drf_check_token
from video.control import *
import logging
from video.models import Video, Moment, Comment, Note

logger = logging.getLogger("django")


@check_token()
def video_list(request, token):
    """
    查看所有视频信息
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    data = {"teacher_data": [], "video_data": []}
    page = request.GET.get("page", PAGINATOR.get("current_page"))
    limit = request.GET.get("limit", PAGINATOR.get("limit"))
    query_field = request.GET.get("query_field")
    try:
        if query_field:
            user = User.objects.filter(openid=token).first()
            if not user:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            user_set = User.objects.filter(username__icontains=query_field).exclude(role="admin").exclude(role="user").order_by("-id")
            new_user_set = data_paginator(user_set, 1, 5)
            for user_obj in new_user_set:
                teacher_dict = dict()
                user_id = user_obj.id
                teacher_id = user_obj.teacher.id
                user_name = user_obj.username
                teacher_dict["user_id"] = user_id
                teacher_dict["teacher_id"] = teacher_id
                teacher_dict["teacher_name"] = user_name
                data["teacher_data"].append(teacher_dict)
            video_set = Video.objects.filter(video_name__icontains=query_field).filter(is_delete=False,
                                                                                       is_issue=True,
                                                                                       status=True).order_by("-id")
            new_videos_set = data_paginator(video_set, page, limit)
            for video in new_videos_set:
                video_dict = dict()
                note_list = list()
                moment_list = list()
                label_list = list()
                notes_set = video.note_set.filter(is_hide=False).order_by('note_time').all()
                moment_set = video.moment_set.all()
                label_set = video.teacher_id.user_id.label_set.all()
                for label_obj in label_set:
                    label_list.append({"label": label_obj.label})
                for note_obj in notes_set:
                    note_list.append({"note_id": note_obj.id,
                                      "note_time": note_obj.note_time,
                                      "is_hide": note_obj.is_hide,
                                      "note_path": note_obj.note_path,
                                      "note_thumb_path": note_obj.note_thumb_path})
                for moment_obj in moment_set:
                    moment_list.append(
                        {"moment_id": moment_obj.id,
                         "moment_time": moment_obj.moment_time,
                         "start_time": moment_obj.start_time,
                         "stop_time": moment_obj.stop_time,
                         "moment_path": moment_obj.moment_path})
                teacher_obj = video.teacher_id
                user_id = teacher_obj.user_id.id
                teacher_id = teacher_obj.id
                teacher_name = teacher_obj.user_id.username
                teacher_school = teacher_obj.school_id.school_name
                relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user).first()
                if relation_user_obj:
                    is_attention = True
                else:
                    is_attention = False
                teacher_dict = {"user_id": user_id,
                                "teacher_id": teacher_id,
                                "teacher_name": teacher_name,
                                "teacher_school": teacher_school,
                                "is_attention": is_attention}
                video_dict["video_id"] = video.id
                video_dict["video_name"] = video.video_name
                video_dict["is_issue"] = video.is_issue
                video_dict["file_path"] = video.file_path
                video_dict["video_date"] = video.video_date
                video_dict["teacher_data"] = teacher_dict
                video_dict["image_path"] = video.image_path
                video_dict["video_status"] = video.status
                video_dict["domain"] = video.teacher_id.school_id.domain
                video_dict["video_notes"] = note_list
                video_dict["video_moments"] = moment_list
                video_dict["label_list"] = label_list
                data["video_data"].append(video_dict)
            data["status"] = 200
            return JsonResponse(data=data)
        else:
            user = User.objects.filter(openid=token).first()
            if not user:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            videos_set = Video.objects.filter(is_delete=False, is_issue=True, status=True).order_by("-id")
            new_videos_set = data_paginator(videos_set, page, limit)
            for video in new_videos_set:
                video_dict = dict()
                note_list = list()
                moment_list = list()
                label_list = list()
                notes_set = video.note_set.filter(is_hide=False).order_by('note_time').all()
                moment_set = video.moment_set.all()
                label_set = video.teacher_id.user_id.label_set.all()
                for label_obj in label_set:
                    label_list.append({"label": label_obj.label})
                for note_obj in notes_set:
                    note_list.append({"note_id": note_obj.id,
                                      "note_time": note_obj.note_time,
                                      "is_hide": note_obj.is_hide,
                                      "note_path": note_obj.note_path,
                                      "note_thumb_path": note_obj.note_thumb_path})
                for moment_obj in moment_set:
                    moment_list.append(
                        {"moment_id": moment_obj.id,
                         "moment_time": moment_obj.moment_time,
                         "start_time": moment_obj.start_time,
                         "stop_time": moment_obj.stop_time,
                         "moment_path": moment_obj.moment_path})
                teacher_obj = video.teacher_id
                user_id = teacher_obj.user_id.id
                teacher_id = teacher_obj.id
                teacher_name = teacher_obj.user_id.username
                teacher_school = teacher_obj.school_id.school_name
                relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user).first()
                if relation_user_obj:
                    is_attention = True
                else:
                    is_attention = False
                teacher_dict = {"user_id": user_id,
                                "teacher_id": teacher_id,
                                "teacher_name": teacher_name,
                                "teacher_school": teacher_school,
                                "is_attention": is_attention}
                video_dict["video_id"] = video.id
                video_dict["video_name"] = video.video_name
                video_dict["is_issue"] = video.is_issue
                video_dict["file_path"] = video.file_path
                video_dict["video_date"] = video.video_date
                video_dict["teacher_data"] = teacher_dict
                video_dict["image_path"] = video.image_path
                video_dict["video_status"] = video.status
                video_dict["domain"] = video.teacher_id.school_id.domain
                video_dict["video_notes"] = note_list
                video_dict["video_moments"] = moment_list
                video_dict["label_list"] = label_list
                data["video_data"].append(video_dict)
            data["status"] = 200
            return JsonResponse(data=data)
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


class CommentListCreateView(ListCreateAPIView):
    """
    METHOD: 请求方法
        post: 给某个视频添加一条评论
        get: 获取某个视频所有评论
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
        video_id = request.GET.get("video_id")
        if not video_id:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            uuid = int(video_id)
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
        video_id = request.POST.get('video_id')
        comment = request.POST.get('comment')
        if not video_id:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            uuid = int(video_id)
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


class CommentDeleteView(DestroyAPIView):
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
        uuid = kwargs.get("uuid")
        if not uuid:
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            uuid = int(uuid)
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


class MomentCreateView(CreateAPIView):
    """
    METHOD: 请求方法
        post: 教师新增精彩时刻
    """

    @drf_check_token()
    def post(self, request, *args, **kwargs):
        """
        教师新增精彩时刻
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        video_id = request.POST.get("video_id")
        second = request.POST.get("second")
        start_time = request.POST.get('start_time')
        stop_time = request.POST.get('stop_time')
        if not all([video_id, second, start_time, stop_time]):
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            second = int(second)
            video_id = int(video_id)
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            if user_obj.role == "user":
                return JsonResponse(data={"error": "无权操作", "status": 400})
            video_obj = Video.objects.filter(id=video_id).first()
            if not video_obj:
                return JsonResponse(data={"error": "该视频不存在", "status": 400})
            if video_obj.teacher_id != user_obj.teacher:
                return JsonResponse(data={"error": "无权操作", "status": 400})
            domain = video_obj.teacher_id.school_id.domain
            dir_name = video_obj.file_name
            response_data = scan_video_image(domain, dir_name, second)
            if not response_data:
                return JsonResponse(data={"error": "设置失败请检查硬件设备和网络", "status": 400})
            image_path = response_data.get("image_path", None)
            if not image_path:
                return JsonResponse(data={"error": "设置失败请检查硬件设备和网络", "status": 400})
            moment_obj = Moment.objects.create(moment_time=second,
                                               moment_path=image_path,
                                               start_time=start_time,
                                               stop_time=stop_time,
                                               video_id=video_obj)
            return JsonResponse(data={"data": {"id": moment_obj.id,
                                               "image_path": moment_obj.moment_path},
                                      "status": 200})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "添加失败", "status": 400})


class MomentDeleteView(DestroyAPIView):
    """
    METHOD: 请求方法
        delete: 教师删除精彩时刻
    """

    @drf_check_token()
    def delete(self, request, *args, **kwargs):
        """
        教师删除精彩时刻
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        token = kwargs.get("token")
        moment_id = kwargs.get("uuid")
        if not all([token, moment_id]):
            return JsonResponse(data={"error": "缺少必传参数", "status": 400})
        try:
            moment_id = int(moment_id)
            user_obj = User.objects.filter(openid=token).first()
            if not user_obj:
                return JsonResponse(data={"error": "用户未注册", "status": 401})
            moment_obj = Moment.objects.filter(id=moment_id).first()
            if not moment_obj:
                return JsonResponse(data={"error": "该回看不存在", "status": 400})
            if moment_obj.video_id.teacher_id.user_id.openid != token:
                return JsonResponse(data={"error": "无权操作", "status": 400})
            moment_obj.delete()
            return JsonResponse(data={"data": {"message": "删除回看成功", "status": 200}})
        except Exception as e:
            logger.error(e)
            return JsonResponse(data={"error": "删除评论失败", "status": 400}, status=400)


@check_token()
def change_video_name(request, token):
    """
    更改视频名字
    :param request:
    :param token: 用户验证，唯一标识
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
def attention_videos(request, token):
    """
    获取关注教师的视频(所有教师的视频)
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    data = {"data": []}
    page = request.GET.get("page", PAGINATOR.get("current_page"))
    limit = request.GET.get("limit", PAGINATOR.get("limit"))
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        teacher_set = RelationUser.objects.filter(user_id=user_obj)
        new_teacher_set = data_paginator(teacher_set, page, limit)
        for teacher_obj in new_teacher_set:
            video_set = Video.objects.filter(teacher_id=teacher_obj.teacher_id,
                                             is_delete=False,
                                             is_issue=True,
                                             status=True).order_by("-id")
            for video_obj in video_set:
                video_dict = dict()
                note_list = list()
                moment_list = list()
                label_list = list()
                notes_set = video_obj.note_set.order_by('note_time').all()
                moment_set = video_obj.moment_set.all()
                label_set = video_obj.teacher_id.user_id.label_set.all()
                for label_obj in label_set:
                    label_list.append({"label": label_obj.label})
                for note_obj in notes_set:
                    note_list.append({"note_id": note_obj.id,
                                      "note_time": note_obj.note_time,
                                      "is_hide": note_obj.is_hide,
                                      "note_path": note_obj.note_path,
                                      "note_thumb_path": note_obj.note_thumb_path})
                for moment_obj in moment_set:
                    moment_list.append(
                        {"moment_id": moment_obj.id,
                         "moment_time": moment_obj.moment_time,
                         "moment_path": moment_obj.moment_path})
                teacher_obj = video_obj.teacher_id
                user_id = teacher_obj.user_id.id
                teacher_id = teacher_obj.id
                teacher_name = teacher_obj.user_id.username
                teacher_school = teacher_obj.school_id.school_name
                teacher_dict = {"user_id": user_id,
                                "teacher_id": teacher_id,
                                "teacher_name": teacher_name,
                                "teacher_school": teacher_school}
                video_dict["video_id"] = video_obj.id
                video_dict["video_name"] = video_obj.video_name
                video_dict["file_path"] = video_obj.file_path
                video_dict["video_date"] = video_obj.video_date
                video_dict["teacher_data"] = teacher_dict
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
def own_videos(request, token):
    """
    获取自己的视频（教师）
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    data = {"data": []}
    page = request.GET.get("page", PAGINATOR.get("current_page"))
    limit = request.GET.get("limit", PAGINATOR.get("limit"))
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "角色不匹配，无权查看", "status": 400})
        video_set = Video.objects.filter(teacher_id=user_obj.teacher, is_delete=False, status=True).order_by("-id")
        new_video_set = data_paginator(video_set, page, limit)
        for video_obj in new_video_set:
            video_dict = dict()
            note_list = list()
            moment_list = list()
            label_list = list()
            notes_set = video_obj.note_set.order_by('note_time').all()
            moment_set = video_obj.moment_set.all()
            label_set = video_obj.teacher_id.user_id.label_set.all()
            for label_obj in label_set:
                label_list.append({"label": label_obj.label})
            for note_obj in notes_set:
                note_list.append({"note_id": note_obj.id,
                                  "note_time": note_obj.note_time,
                                  "is_hide": note_obj.is_hide,
                                  "note_path": note_obj.note_path,
                                  "note_thumb_path": note_obj.note_thumb_path})
            for moment_obj in moment_set:
                moment_list.append(
                    {"moment_id": moment_obj.id,
                     "moment_time": moment_obj.moment_time,
                     "start_time": moment_obj.start_time,
                     "stop_time": moment_obj.stop_time,
                     "moment_path": moment_obj.moment_path})
            teacher_obj = video_obj.teacher_id
            user_id = teacher_obj.user_id.id
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.user_id.username
            teacher_school = teacher_obj.school_id.school_name
            relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user_obj).first()
            if relation_user_obj:
                is_attention = True
            else:
                is_attention = False
            teacher_dict = {"user_id": user_id,
                            "teacher_id": teacher_id,
                            "teacher_name": teacher_name,
                            "teacher_school": teacher_school,
                            "is_attention": is_attention}
            video_dict["video_id"] = video_obj.id
            video_dict["video_name"] = video_obj.video_name
            video_dict["is_issue"] = video_obj.is_issue
            video_dict["file_path"] = video_obj.file_path
            video_dict["video_date"] = video_obj.video_date
            video_dict["teacher_data"] = teacher_dict
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
def video_start(request, token):
    """
    开始录制视频
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    class_id = request.POST.get('class_id')
    if not class_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "非教师用户无权录制", "status": 400})
        class_obj = Class.objects.filter(id=int(class_id)).first()
        if not class_obj:
            return JsonResponse(data={"error": "该教室不存在", "status": 400})
        equipment_obj = Equipment.objects.filter(class_id=class_obj).first()
        if not equipment_obj:
            return JsonResponse(data={"error": "该教室未绑定录制设备", "status": 400})
        if equipment_obj.school_id != user_obj.teacher.school_id:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        if equipment_obj.status != "available":
            return JsonResponse(data={"error": "当前教室录制设备被占用,开始录制失败", "status": 400})
        domain = equipment_obj.school_id.domain
        mac_address = equipment_obj.mac_address
        response_data = start_recording(domain, mac_address)
        if not response_data:
            return JsonResponse(data={"error": "录制失败请检查硬件设备和网络", "status": 400})
        file_name = response_data.get("file_name", None)
        if not file_name:
            return JsonResponse(data={"error": "录制失败请检查硬件设备和网络", "status": 400})
        equipment_obj.status = "in_use"
        equipment_obj.teacher_id = user_obj.teacher
        video_date = int(time.time())
        video_date_str = custom_time(video_date)
        file_path = "/fsdata/videos/" + file_name + "/" + file_name
        image_path = "/fsdata/videos/" + file_name + "/cover.png"
        video_obj = Video.objects.create(video_name=video_date_str,
                                         file_name=file_name,
                                         file_path=file_path,
                                         image_path=image_path,
                                         video_date=video_date,
                                         teacher_id=user_obj.teacher)
        equipment_obj.save()
        return JsonResponse(data={"data": {"id": video_obj.id,
                                           "video_name": video_date, },
                                  "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "开始录制失败", "status": 400})


@check_token()
def video_stop(request, token):
    """
    结束录制视频
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    class_id = request.POST.get('class_id')
    video_id = request.POST.get('video_id')
    if not all([class_id, video_id]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "无权操作", "status": 400})
        class_obj = Class.objects.filter(id=int(class_id)).first()
        if not class_obj:
            return JsonResponse(data={"error": "该教室不存在", "status": 400})
        equipment_obj = Equipment.objects.filter(class_id=class_obj).first()
        if not equipment_obj:
            return JsonResponse(data={"error": "该教室未绑定录制设备", "status": 400})
        if equipment_obj.school_id != user_obj.teacher.school_id:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        if equipment_obj.status != "in_use":
            return JsonResponse(data={"error": "结束录制失败，该教室不在录制中", "status": 400})
        domain = equipment_obj.school_id.domain
        mac_address = equipment_obj.mac_address
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "结束录制失败，该视频不存在", "status": 400})
        file_name = video_obj.file_name
        response_data = stop_recording(domain, file_name, mac_address)
        response_status = response_data.get("status", None)
        if response_status is not 200:
            return JsonResponse(data={"error": "结束录制失败请检查硬件设备和网络",
                                      "status": 400})
        note_path_list = response_data.get("data").get("note_path")
        for i in note_path_list:
            note_path = i.get("note_path")
            note_thumb_path = i.get("note_thumb_path")
            note_time = i.get("note_time")
            Note.objects.create(note_time=note_time,
                                note_path=note_path,
                                note_thumb_path=note_thumb_path,
                                video_id=video_obj)
        equipment_obj.status = "available"
        equipment_obj.teacher_id = None
        video_obj.status = True
        image_path = video_obj.image_path
        equipment_obj.save()
        video_obj.save()
        return JsonResponse(data={"data": {"image_path": image_path},
                                  "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "结束录制失败", "status": 400})


@check_token()
def video_issue(request, token):
    """
    发布视频功能
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    video_id = request.POST.get('video_id')
    if not video_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "无权操作", "status": 400})
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "该视频不存在", "status": 400})
        if video_obj.teacher_id != user_obj.teacher:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        video_obj.is_issue = True
        video_obj.save()
        return JsonResponse(data={"message": "发布视频成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "发布视频失败", "status": 400})


@check_token()
def video_delete(request, token):
    """
    删除视频功能
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    video_id = request.POST.get('video_id')
    if not video_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "无权操作", "status": 400})
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "该视频不存在", "status": 400})
        if video_obj.teacher_id != user_obj.teacher:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        video_obj.is_delete = True
        video_obj.save()
        return JsonResponse(data={"message": "删除视频成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "删除视频失败", "status": 400})


@check_token()
def get_classes(request, token):
    """
    小程序获取所有教室
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    data = {"data": []}
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "无权查看", "status": 400})
        school_obj = user_obj.teacher.school_id
        grade_set = Class.objects.values_list("grade_name", flat=True).distinct()
        for grade_name in grade_set:
            grade_dict = dict()
            grade_list = list()
            class_set = Class.objects.filter(school_id=school_obj, grade_name=grade_name)
            for class_obj in class_set:
                class_dict = dict()
                equipment_dict = dict()
                class_dict["id"] = class_obj.id
                class_dict["class_name"] = class_obj.class_name
                class_dict["grade_name"] = class_obj.grade_name
                equipment_obj = Equipment.objects.filter(class_id=class_obj).first()
                if equipment_obj:
                    teacher_dict = dict()
                    equipment_dict["equipment_id"] = class_obj.equipment.id
                    equipment_dict["status"] = class_obj.equipment.status
                    equipment_dict["mac_address"] = class_obj.equipment.mac_address
                    if equipment_obj.teacher_id:
                        teacher_dict["user_id"] = class_obj.equipment.teacher_id.user_id.id
                        teacher_dict["teacher_name"] = class_obj.equipment.teacher_id.user_id.username
                    equipment_dict["teacher_data"] = teacher_dict
                class_dict["equipment_dict"] = equipment_dict
                grade_list.append(class_dict)
            grade_dict["grade_name"] = grade_name
            grade_dict["grade_class"] = grade_list
            data["data"].append(grade_dict)
        data["domain"] = school_obj.domain
        data["status"] = 200
        return JsonResponse(data=data)

    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取教室信息失败", "status": 400})


@check_token()
def is_hide_blackboard(request, token):
    """
    教师设置是否隐藏版书
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    note_id = request.POST.get('note_id')
    is_hide = request.POST.get('is_hide')
    if not all([note_id, is_hide]):
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        is_hide = int(is_hide)
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        if user_obj.role == "user":
            return JsonResponse(data={"error": "无权操作", "status": 400})
        note_obj = Note.objects.filter(id=note_id).first()
        if not note_obj:
            return JsonResponse(data={"error": "版书不存在", "status": 400})
        if note_obj.video_id.teacher_id != user_obj.teacher:
            return JsonResponse(data={"error": "无权操作", "status": 400})
        note_obj.is_hide = is_hide
        note_obj.save()
        return JsonResponse(data={"message": "操作成功", "status": 200})
    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "操作失败", "status": 400})


@check_token()
def video_details(request, token, **kwargs):
    """
    查询视频详情
    :param request:
    :param token: 用户验证，唯一标识
    :param kwargs:
    :return:
    """
    video_id = kwargs.get("uuid")
    if not video_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        user_obj = User.objects.filter(openid=token).first()
        if not user_obj:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "该视频不存在", "status": 400})
        data = dict()
        video_dict = dict()
        note_list = list()
        moment_list = list()
        label_list = list()
        notes_set = video_obj.note_set.order_by('note_time').all()
        moment_set = video_obj.moment_set.all()
        label_set = video_obj.teacher_id.user_id.label_set.all()
        for label_obj in label_set:
            label_list.append({"label": label_obj.label})
        for note_obj in notes_set:
            note_list.append({"note_id": note_obj.id,
                              "note_time": note_obj.note_time,
                              "is_hide": note_obj.is_hide,
                              "note_path": note_obj.note_path,
                              "note_thumb_path": note_obj.note_thumb_path})
        for moment_obj in moment_set:
            moment_list.append(
                {"moment_id": moment_obj.id,
                 "moment_time": moment_obj.moment_time,
                 "start_time": moment_obj.start_time,
                 "stop_time": moment_obj.stop_time,
                 "moment_path": moment_obj.moment_path})
        teacher_obj = video_obj.teacher_id
        user_id = teacher_obj.user_id.id
        teacher_id = teacher_obj.id
        teacher_name = teacher_obj.user_id.username
        teacher_school = teacher_obj.school_id.school_name
        relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user_obj).first()
        if relation_user_obj:
            is_attention = True
        else:
            is_attention = False
        teacher_dict = {"user_id": user_id,
                        "teacher_id": teacher_id,
                        "teacher_name": teacher_name,
                        "teacher_school": teacher_school,
                        "is_attention": is_attention}
        video_dict["video_id"] = video_obj.id
        video_dict["video_name"] = video_obj.video_name
        video_dict["is_issue"] = video_obj.is_issue
        video_dict["file_path"] = video_obj.file_path
        video_dict["video_date"] = video_obj.video_date
        video_dict["teacher_data"] = teacher_dict
        video_dict["image_path"] = video_obj.image_path
        video_dict["video_status"] = video_obj.status
        video_dict["domain"] = video_obj.teacher_id.school_id.domain
        video_dict["video_notes"] = note_list
        video_dict["video_moments"] = moment_list
        video_dict["label_list"] = label_list
        data["data"] = video_dict
        data["status"] = 200
        return JsonResponse(data=data)

    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


def video_share(request, **kwargs):
    """
    查询分享的视频信息，无token验证
    :param request:
    :param kwargs:
    :return:
    """
    video_id = kwargs.get("uuid")
    if not video_id:
        return JsonResponse(data={"error": "缺少必传参数", "status": 400})
    try:
        video_obj = Video.objects.filter(id=video_id).first()
        if not video_obj:
            return JsonResponse(data={"error": "该视频不存在", "status": 400})
        data = dict()
        video_dict = dict()
        note_list = list()
        moment_list = list()
        label_list = list()
        notes_set = video_obj.note_set.filter(is_hide=False).order_by('note_time').all()
        moment_set = video_obj.moment_set.all()
        label_set = video_obj.teacher_id.user_id.label_set.all()
        for label_obj in label_set:
            label_list.append({"label": label_obj.label})
        for note_obj in notes_set:
            note_list.append({"note_id": note_obj.id,
                              "note_time": note_obj.note_time,
                              "is_hide": note_obj.is_hide,
                              "note_path": note_obj.note_path,
                              "note_thumb_path": note_obj.note_thumb_path})
        for moment_obj in moment_set:
            moment_list.append(
                {"moment_id": moment_obj.id,
                 "moment_time": moment_obj.moment_time,
                 "start_time": moment_obj.start_time,
                 "stop_time": moment_obj.stop_time,
                 "moment_path": moment_obj.moment_path})
        teacher_obj = video_obj.teacher_id
        user_id = teacher_obj.user_id.id
        teacher_id = teacher_obj.id
        teacher_name = teacher_obj.user_id.username
        teacher_school = teacher_obj.school_id.school_name
        teacher_dict = {"user_id": user_id,
                        "teacher_id": teacher_id,
                        "teacher_name": teacher_name,
                        "teacher_school": teacher_school}
        video_dict["video_id"] = video_obj.id
        video_dict["video_name"] = video_obj.video_name
        video_dict["is_issue"] = video_obj.is_issue
        video_dict["file_path"] = video_obj.file_path
        video_dict["video_date"] = video_obj.video_date
        video_dict["teacher_data"] = teacher_dict
        video_dict["image_path"] = video_obj.image_path
        video_dict["video_status"] = video_obj.status
        video_dict["domain"] = video_obj.teacher_id.school_id.domain
        video_dict["video_notes"] = note_list
        video_dict["video_moments"] = moment_list
        video_dict["label_list"] = label_list
        data["data"] = video_dict
        data["status"] = 200
        return JsonResponse(data=data)

    except Exception as e:
        logger.error(e)
        return JsonResponse(data={"error": "获取数据失败", "status": 400})


@check_token()
def teacher_video_list(request, token, **kwargs):
    """
    查看某个教师的所有视频
    :param request:
    :param token: 用户验证，唯一标识
    :return:
    """
    data = {"data": []}
    teacher_id = kwargs.get("uuid")
    page = request.GET.get("page", PAGINATOR.get("current_page"))
    limit = request.GET.get("limit", PAGINATOR.get("limit"))
    try:
        user = User.objects.filter(openid=token).first()
        if not user:
            return JsonResponse(data={"error": "用户未注册", "status": 401})
        teacher_object = Teacher.objects.filter(id=teacher_id).first()
        if not teacher_object:
            return JsonResponse(data={"error": "该教师不存在", "status": 400})
        videos_set = Video.objects.filter(teacher_id=teacher_object,
                                          is_delete=False,
                                          status=True,
                                          is_issue=True).order_by("-id")
        new_videos_set = data_paginator(videos_set, page, limit)
        for video in new_videos_set:
            video_dict = dict()
            note_list = list()
            moment_list = list()
            label_list = list()
            notes_set = video.note_set.filter(is_hide=False).order_by('note_time').all()
            moment_set = video.moment_set.all()
            label_set = video.teacher_id.user_id.label_set.all()
            for label_obj in label_set:
                label_list.append({"label": label_obj.label})
            for note_obj in notes_set:
                note_list.append({"note_id": note_obj.id,
                                  "note_time": note_obj.note_time,
                                  "is_hide": note_obj.is_hide,
                                  "note_path": note_obj.note_path,
                                  "note_thumb_path": note_obj.note_thumb_path})
            for moment_obj in moment_set:
                moment_list.append(
                    {"moment_id": moment_obj.id,
                     "moment_time": moment_obj.moment_time,
                     "start_time": moment_obj.start_time,
                     "stop_time": moment_obj.stop_time,
                     "moment_path": moment_obj.moment_path})
            teacher_obj = video.teacher_id
            user_id = teacher_obj.user_id.id
            teacher_id = teacher_obj.id
            teacher_name = teacher_obj.user_id.username
            teacher_school = teacher_obj.school_id.school_name
            relation_user_obj = RelationUser.objects.filter(teacher_id=teacher_obj, user_id=user).first()
            if relation_user_obj:
                is_attention = True
            else:
                is_attention = False
            teacher_dict = {"user_id": user_id,
                            "teacher_id": teacher_id,
                            "teacher_name": teacher_name,
                            "teacher_school": teacher_school,
                            "is_attention": is_attention}
            video_dict["video_id"] = video.id
            video_dict["video_name"] = video.video_name
            video_dict["is_issue"] = video.is_issue
            video_dict["file_path"] = video.file_path
            video_dict["video_date"] = video.video_date
            video_dict["teacher_data"] = teacher_dict
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
