from django.db import models
from django.contrib.auth.hashers import make_password
from common.models.timestamped import TimeStampedModel
from account.models.family import Family
from .notify_type import MstNotifyType
from .notify_method import MstNotifyMethod


class NotificationLog(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_logs')
    notify_type = models.ForeignKey(MstNotifyType, on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_logs')
    notify_method = models.ForeignKey(MstNotifyMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_logs')
    group_id = models.CharField(max_length=128, null=True, blank=True)
    notify_content = models.TextField(null=False, blank=False)
    success_flag = models.BooleanField(null=False, blank=False)
    response_code = models.CharField(max_length=32, null=True, blank=True)
    response_message = models.TextField(null=True, blank=True)
    action_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        family_name = self.family.family_authentication_id if self.family else "不明"
        return f"{family_name}（{self.action_at}）"

    class Meta:
        db_table = 't_notification_log'
