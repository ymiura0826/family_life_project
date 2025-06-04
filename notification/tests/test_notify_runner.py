from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from account.models.family import Family
from notification.models.notify_schedule import NotifySchedule
from notification.models.notify_log import NotificationLog
from notification.models.notify_type import MstNotifyType
from notification.models.notify_method import MstNotifyMethod
from scripts.notify_runner import run_line_notifications


class NotifyRunnerTests(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            family_authentication_id="testfamily",
            family_password="pass",
            line_notify_id="dummy_group_id"
        )
        self.ntype = MstNotifyType.objects.create(id=1, name="milk", order_id=1)
        self.method = MstNotifyMethod.objects.create(id=3, name="line_official", order_id=1)

        self.schedule = NotifySchedule.objects.create(
            family=self.family,
            notify_type=self.ntype,
            notify_method=self.method,
            notify_content="テスト通知",
            schedule_at=timezone.now()
        )

    @patch("scripts.notify_runner.send_line_message")
    def test_notification_sent_and_logged(self, mock_send):
        # モックで通知成功を強制
        mock_send.return_value = {
            "status_code": 200,
            "response": {"message": "ok"},
            "success": True
        }

        run_line_notifications()

        logs = NotificationLog.objects.filter(family=self.family)
        self.assertEqual(logs.count(), 1)
        self.assertTrue(logs.first().success_flag)
        self.assertEqual(logs.first().notify_content, "テスト通知")
