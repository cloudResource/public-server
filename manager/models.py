from django.db import models

from user.models import User


# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100, null=True, help_text="project_name")
    app_id = models.CharField(max_length=100, null=True, help_text="app_id")
    app_secret = models.CharField(max_length=100, null=True, help_text="app_secret")

    class Meta:
        db_table = "tb_project"


class School(models.Model):
    school_name = models.CharField(max_length=64, null=True, help_text="学校名称")
    admin_user_id = models.OneToOneField(User, db_column="admin_user_id")
    domain = models.CharField(max_length=64, null=True, help_text="学校域名")

    class Meta:
        db_table = "tb_school"


class Teacher(models.Model):
    rank = models.CharField(max_length=16, null=True, help_text="教师等级")
    school_id = models.ForeignKey(School, null=True, db_column="school_id")
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, db_column="user_id")

    class Meta:
        db_table = "tb_teacher"


class RelationUser(models.Model):
    user_id = models.ForeignKey(User, db_column="user_id")
    teacher_id = models.ForeignKey(Teacher, db_column="teacher_id")

    class Meta:
        db_table = "tb_relation_user"


class Class(models.Model):
    class_name = models.CharField(max_length=64, null=True, help_text="班级名称")
    grade_name = models.CharField(max_length=64, null=True, help_text="年级名称")
    school_id = models.ForeignKey(School, null=True, db_column="school_id")

    class Meta:
        db_table = "tb_class"


class Equipment(models.Model):
    mac_address = models.CharField(max_length=100, unique=True, null=True, help_text="设备mac地址")
    teacher_id = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, db_column="teacher_id")
    class_id = models.OneToOneField(Class, on_delete=models.SET_NULL, blank=True, null=True,
                                    db_column="class_id", related_name='equipment')
    status = models.CharField(max_length=16, default="available", help_text="设备的状态")  # available: 可用, in_use: 使用中
    real_url = models.CharField(max_length=100, null=True, help_text="实时视频地址")
    school_id = models.ForeignKey(School, null=True, db_column="school_id")  # 设备所属学校

    class Meta:
        db_table = "tb_equipment"
