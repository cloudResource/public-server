from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=32, null=True, help_text="用户名")
    mobile = models.CharField(max_length=32, null=True, unique=True, help_text="用户注册手机号")
    password = models.CharField(max_length=32, null=True, help_text="用户密码")
    role = models.CharField(max_length=32,
                            default="user",
                            help_text="角色") # {"role": ["user", "admin", "teacher", "admin_teacher"]}
    openid = models.CharField(max_length=64, null=True, unique=True, help_text="微信唯一标识")

    class Meta:
        db_table = 'tb_user'


class Label(models.Model):
    label = models.CharField(max_length=32, null=True, help_text="标签内容")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column="user_id")

    class Meta:
        db_table = "tb_label"
