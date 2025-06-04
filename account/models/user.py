from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models.timestamped import TimeStampedModel
from .family import Family


class CustomUser(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)# メールアドレスをログインIDとして使う（オプション）
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')# 家族への外部キー（論理削除されたFamilyでも保持できるよう SET_NULL にしておく）

    def __str__(self):
        return f"{self.username} ({self.email})"

    class Meta:
        db_table = 't_user'