from django.db import models

# Create your models here.
# from user.models import User
from manager.models import Teacher
from user.models import User


class Video(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="视频名称")
    end_time = models.IntegerField(help_text="视频结束时间戳")
    size = models.IntegerField(help_text="视频文件大小")
    is_delete = models.BooleanField(default=False, help_text="视频的逻辑删除")
    status = models.BooleanField(default=False, help_text="视频的状态")
    # video_owner_id = models.OneToOneField(User, on_delete=models.CASCADE, db_column="video_owner_id")
    image_path = models.CharField(max_length=100, null=True, help_text="图片播放地址")
    teacher_id = models.ForeignKey(Teacher, null=True, db_column="teacher_id")

    class Meta:
        db_table = "tb_video"


class Note(models.Model):
    note_time = models.IntegerField(help_text="版书时间秒", null=True)
    note_path = models.CharField(max_length=100, help_text="版书路径")
    video_id = models.ForeignKey(Video, null=True, db_column="video_id")

    class Meta:
        db_table = "tb_note"


class Moment(models.Model):
    moment_time = models.IntegerField(help_text="回放时间秒", null=True)
    moment_path = models.CharField(max_length=100, help_text="精彩回放图片")
    video_id = models.ForeignKey(Video, null=True, db_column="video_id")

    class Meta:
        db_table = "tb_moment"


class Comment(models.Model):
    comment = models.CharField(max_length=100, null=True, help_text="用户评论信息")
    like = models.IntegerField(help_text="评论点赞数")
    video_id = models.ForeignKey(Video, null=True, db_column="video_id")

    class Meta:
        db_table = "tb_comment"


class VideoLabel(models.Model):
    video_label = models.CharField(max_length=100, help_text="视频标签")
    video_id = models.ForeignKey(Video, null=True, db_column="video_id")

    class Meta:
        db_table = "tb_video_label"
