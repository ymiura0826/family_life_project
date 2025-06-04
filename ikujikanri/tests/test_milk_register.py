from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, timezone as dt_timezone
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone

from account.models.family import Family
from account.models.child import Child
from account.models.sex import MstSex
from ikujikanri.models.milk_record import MilkRecord
from ikujikanri.models.milk_type import MstMilkType
from notification.models.notify_schedule import NotifySchedule
from notification.models.notify_type import MstNotifyType
from notification.models.notify_method import MstNotifyMethod

User = get_user_model()

class MilkRegisterViewTests(TestCase):
    def setUp(self):
        self.sex = MstSex.objects.create(id=1, name='男の子', order_id=1)
        self.milk_type_breast = MstMilkType.objects.create(id=1, name='母乳', order_id=1)
        self.milk_type_powder = MstMilkType.objects.create(id=2, name='粉ミルク', order_id=2)
        self.notify_type = MstNotifyType.objects.create(id=1, name='milk', order_id=1)
        self.notify_method = MstNotifyMethod.objects.create(id=1, name='email', order_id=1)

        self.family = Family.objects.create(family_authentication_id="fam001", family_password="password")
        self.user = User.objects.create_user(username="testuser", password="testpass", family=self.family)
        self.client.login(username="testuser", password="testpass")

        self.child = Child.objects.create(name="テスト太郎", birth_date="2020-01-01", sex=self.sex, family=self.family)
        self.other_family = Family.objects.create(family_authentication_id="fam002", family_password="password")
        self.other_child = Child.objects.create(name="他人の子", birth_date="2020-01-01", sex=self.sex, family=self.other_family)

    def post_data(self, child_id, data):
        url = reverse("milk_register", kwargs={"child_id": child_id})
        return self.client.post(url, data)

    def test_register_breast_milk_success(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_breast.id,
            "left_breast_minutes": 5,
            "right_breast_minutes": "",
            "amount": "",
            "notify_flag": False,
        }
        response = self.post_data(self.child.child_id, data)
        self.assertRedirects(response, reverse("ikujikanri_top"))
        self.assertEqual(MilkRecord.objects.count(), 1)

    def test_register_powder_milk_success(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "amount": 100,
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "notify_flag": False,
        }
        response = self.post_data(self.child.child_id, data)
        self.assertRedirects(response, reverse("ikujikanri_top"))
        self.assertEqual(MilkRecord.objects.count(), 1)

    def test_validation_error_breast_milk_no_minutes(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_breast.id,
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "amount": "",
            "notify_flag": False,
        }
        response = self.post_data(self.child.child_id, data)
        self.assertContains(response, "母乳の場合は左右いずれかの授乳時間を入力してください。")
        self.assertEqual(MilkRecord.objects.count(), 0)

    def test_validation_error_powder_milk_no_amount(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "amount": "",
            "notify_flag": False,
        }
        response = self.post_data(self.child.child_id, data)
        self.assertContains(response, "粉ミルクまたは搾乳の場合は量を入力してください。")
        self.assertEqual(MilkRecord.objects.count(), 0)

    def test_notify_schedule_created(self):
        jst = get_current_timezone()

        # timezone.now() は aware → naive に変換してから make_aware する
        naive_now = timezone.now().astimezone(jst).replace(tzinfo=None)
        next_milk_at_jst = make_aware(naive_now + timedelta(hours=3), timezone=jst)
        expected_utc = (next_milk_at_jst - timedelta(minutes=30)).astimezone(dt_timezone.utc).replace(second=0, microsecond=0)

        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "amount": 100,
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "notify_flag": True,
            "next_milk_at": next_milk_at_jst.strftime("%Y-%m-%dT%H:%M"),
        }

        response = self.post_data(self.child.child_id, data)
        self.assertRedirects(response, reverse("ikujikanri_top"))

        notify = NotifySchedule.objects.first()
        self.assertEqual(
            notify.schedule_at.replace(second=0, microsecond=0),
            expected_utc
        )

    def test_notify_flag_false_does_not_create_schedule(self):
        next_milk_time = timezone.now() + timedelta(hours=3)
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "amount": 100,
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "notify_flag": False,
            "next_milk_at": next_milk_time.strftime("%Y-%m-%dT%H:%M"),
        }
        response = self.post_data(self.child.child_id, data)
        self.assertRedirects(response, reverse("ikujikanri_top"))
        self.assertEqual(NotifySchedule.objects.count(), 0)

    def test_access_other_family_child_returns_404(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "amount": 100,
            "notify_flag": False,
        }
        response = self.post_data(self.other_child.child_id, data)
        self.assertEqual(response.status_code, 404)
