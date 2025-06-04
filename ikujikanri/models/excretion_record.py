from django.db import models
from common.models.timestamped import TimeStampedModel
from account.models.child import Child
from .excretion_type import MstExcretionType


class ExcretionRecord(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    child = models.ForeignKey(Child, to_field='child_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='excretion_records')
    excretion_type = models.ForeignKey(MstExcretionType, on_delete=models.SET_NULL, null=True, blank=True, related_name='excretion_records')
    memo = models.CharField(max_length=200, blank=True)  # blank=True を追加して空メモも許容
    action_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        child_name = self.child.name if self.child else "不明"
        return f"{child_name}（{self.action_at}）"

    class Meta:
        db_table = 't_excretion_record'
