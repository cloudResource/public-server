from django.db import models

from user.models import User


# Create your models here.

class School(models.Model):
    school_name = models.CharField(max_length=64, null=True, help_text="学校名称")
    admin_user_id = models.OneToOneField(User, db_column="admin_user_id")

    class Meta:
        db_table = "tb_school"


class Teacher(models.Model):
    name = models.CharField(max_length=16, null=True, help_text="教师名字")
    rank = models.CharField(max_length=16, null=True, help_text="教师等级")
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, db_column="user_id")
    school_id = models.ForeignKey(School, null=True, db_column="school_id")

    class Meta:
        db_table = "tb_teacher"


class Grade(models.Model):
    grade_name = models.CharField(max_length=64, null=True, help_text="年级名称")
    school_id = models.ForeignKey(School, null=True, db_column="school_id")

    class Meta:
        db_table = "tb_grade"


class Class(models.Model):
    class_name = models.CharField(max_length=64, null=True, help_text="班级名称")
    grade_id = models.ForeignKey(Grade, null=True, db_column="grade_id")

    class Meta:
        db_table = "tb_class"


class Equipment(models.Model):
    use_teacher = models.ForeignKey(Grade, null=True, db_column="_id")
    equipment_url = models.CharField(max_length=100, null=True, help_text="设备地址")
    teacher_id = models.ForeignKey(Teacher, null=True, db_column="teacher_id")
    class_id = models.ForeignKey(Class, null=True, db_column="class_id")
    status = models.BooleanField(default=True, help_text="设备的状态")
    real_url = models.CharField(max_length=100, null=True, help_text="实时视频地址")

    class Meta:
        db_table = "tb_equipment"
