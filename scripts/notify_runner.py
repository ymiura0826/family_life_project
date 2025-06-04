# scripts/notify_runner.py

import os
import sys
import django
import datetime

# Djangoの設定を読み込む
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils.timezone import now, localtime
from django.utils.timezone import now as timezone_now
from notification.models.notify_schedule import NotifySchedule
from notification.models.notify_log import NotificationLog
from notification.services.line_message import send_line_message

def run_line_notifications():
    now_dt = now()
    schedules = NotifySchedule.objects.filter(
        schedule_at__lte=now_dt,
        notify_method__id=3,  # ← 通知手段が「line_official」のものに限定
        deleted_at__isnull=True
    )

    print(f"[{localtime(now_dt)}] 通知対象: {schedules.count()} 件")

    for schedule in schedules:
        family = schedule.family
        group_id = getattr(family, "line_notify_id", None)

        if not group_id:
            print(f"⚠️ family_id={family.family_id} に group_id 未設定 → スキップ")
            continue

        result = send_line_message(group_id, schedule.notify_content)
        now_exec_time = now()

        # ✅ ログ保存処理
        NotificationLog.objects.create(
            family=family,
            notify_type=schedule.notify_type,
            notify_method=schedule.notify_method,
            group_id=group_id,
            notify_content=schedule.notify_content,
            success_flag=result["success"],
            response_code=str(result["status_code"]),
            response_message=str(result["response"]),
            action_at=now_exec_time
        )

        if result["success"]:
            print(f"✅ 通知成功 → {group_id}: {schedule.notify_content}")
        else:
            print(f"❌ 通知失敗 → {group_id}: {result['response']}")

        # 再送防止（成功／失敗に関係なく論理削除する）
        schedule.deleted_at = timezone_now()
        schedule.save()

if __name__ == "__main__":
    run_line_notifications()
