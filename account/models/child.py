from django.db import models
from django.contrib.auth.hashers import make_password
from common.models.timestamped import TimeStampedModel
from .family import Family
from .sex import MstSex


class Child(TimeStampedModel):
    child_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    birth_date = models.DateField()
    sex = models.ForeignKey(MstSex, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    def __str__(self):
        return f"{self.name}（{self.family.family_authentication_id if self.family else '所属なし'}）"

    class Meta:
        db_table = 't_child'