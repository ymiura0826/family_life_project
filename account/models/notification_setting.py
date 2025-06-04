from django.db import models
from common.models.timestamped import TimeStampedModel
from .family import Family
from notification.models.notify_method import MstNotifyMethod


class NotificationSetting(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_settings')
    notify_method =  models.ForeignKey(MstNotifyMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_settings')
    enable_notify_flag = models.BooleanField(null=False,blank=False)
    
    def __str__(self):
        return f"{self.family.family_authentication_id if self.family else '不明'}（{self.notify_method.name if self.notify_method else '未設定'}）"

    class Meta:
        db_table = 't_notification_setting'