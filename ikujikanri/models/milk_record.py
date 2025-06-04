from django.db import models
from common.models.timestamped import TimeStampedModel
from account.models.child import Child
from .milk_type import MstMilkType


class MilkRecord(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    child = models.ForeignKey(Child, to_field='child_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='milk_records')
    milk_type =  models.ForeignKey(MstMilkType, on_delete=models.SET_NULL, null=True, blank=True, related_name='milk_records')
    amount = models.IntegerField(null=True, blank=True)
    left_breast_minutes = models.IntegerField(null=True, blank=True)
    right_breast_minutes = models.IntegerField(null=True, blank=True)
    action_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        child_name = self.child.name if self.child else "不明"
        return f"{child_name}（{self.action_at}）"

    class Meta:
        db_table = 't_milk_record'