# scripts/load_notify_master.py（例）
from notification.models import MstNotifyType, MstNotifyMethod

MstNotifyType.objects.get_or_create(name='ミルク時間', defaults={'order_id': 1})
MstNotifyMethod.objects.get_or_create(name='LINE Notify', defaults={'order_id': 1})
MstNotifyMethod.objects.get_or_create(name='メール', defaults={'order_id': 2})
