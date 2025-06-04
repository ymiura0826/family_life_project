from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now) #データが初めて保存された日時を自動で記録
    updated_at = models.DateTimeField(auto_now=True) #モデルが更新されるたびに、自動で現在時刻に上書き
    deleted_at = models.DateTimeField(null=True, blank=True) #論理削除（soft delete）を実現するためのフィールド

    class Meta:
        abstract = True #継承先に共通の機能を提供するベースクラスにできる
