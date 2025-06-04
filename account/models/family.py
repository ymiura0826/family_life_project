from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from common.models.timestamped import TimeStampedModel


class Family(TimeStampedModel):
    family_id = models.BigAutoField(primary_key=True)
    family_authentication_id = models.CharField(max_length=50, unique=True)
    family_password = models.CharField(max_length=128)
    line_notify_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"Family {self.family_authentication_id}" # f"" = concat処理

    def save(self, *args, **kwargs):
        # パスワードがハッシュ化されていなければハッシュ化する
        if self.family_password and not self.family_password.startswith('pbkdf2_'):
            self.family_password = make_password(self.family_password)
        super().save(*args, **kwargs) #親を呼び出して保存処理をかける。自分で作ったsaveではDB保存はやってくれない。

    class Meta:
        db_table = 't_family'