from django.db import models
from account.models.family import Family
from common.models.timestamped import TimeStampedModel
from .notify_type import MstNotifyType
from .notify_method import MstNotifyMethod


class NotifySchedule(TimeStampedModel):
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_schedules')
    notify_type =  models.ForeignKey(MstNotifyType, on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_schedules')
    notify_method =  models.ForeignKey(MstNotifyMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='notification_schedules')
    schedule_at = models.DateTimeField()
    notify_content = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        family_name = self.family.family_authentication_id if self.family else "不明"
        return f"{family_name}（{self.schedule_at}）"

    class Meta:
        db_table = 't_notify_schedule'
        ordering = ['schedule_at']
