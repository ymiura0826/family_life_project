from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family
from account.models.child import Child
from ikujikanri.models.milk_record import MilkRecord
from ikujikanri.models.excretion_record import ExcretionRecord
from ikujikanri.models.excretion_type import MstExcretionType
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

User = get_user_model()

class IkujiTopViewTests(TestCase):
    def setUp(self):
        self.pee = MstExcretionType.objects.create(order_id=1, name="おしっこ")
        self.poo = MstExcretionType.objects.create(order_id=2, name="うんち")
        self.url = reverse("ikujikanri_top")
        self.family = Family.objects.create(
            family_authentication_id="fam001",
            family_password="testpass"
        )
        self.user = User.objects.create_user(
            username="parent", password="pass123", family=self.family
        )
        self.client.login(username="parent", password="pass123")

        self.pee = MstExcretionType.objects.get(name="おしっこ")
        self.poo = MstExcretionType.objects.get(name="うんち")

        self.today = datetime.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.today_dt = make_aware(datetime.combine(self.today, datetime.min.time()))
        self.yesterday_dt = make_aware(datetime.combine(self.yesterday, datetime.min.time()))

    def test_no_children(self):
        response = self.client.get(self.url)
        self.assertContains(response, "子ども情報が登録されていません。")

    def test_child_with_no_records(self):
        Child.objects.create(name="赤ちゃんA", birth_date="2024-01-01", family=self.family)
        response = self.client.get(self.url)
        self.assertContains(response, "記録なし")
        self.assertContains(response, "おしっこ 0 回、うんち 0 回")

    def test_child_with_records(self):
        child = Child.objects.create(name="赤ちゃんB", birth_date="2024-01-01", family=self.family)

        MilkRecord.objects.create(child=child, action_at=self.yesterday_dt)
        ExcretionRecord.objects.create(child=child, action_at=self.today_dt, excretion_type=self.pee)
        ExcretionRecord.objects.create(child=child, action_at=self.yesterday_dt, excretion_type=self.poo)

        response = self.client.get(self.url)
        self.assertContains(response, "赤ちゃんB")
        self.assertContains(response, self.yesterday_dt.strftime("%B %#d, %Y"))
        self.assertContains(response, "おしっこ 1 回、うんち 0 回")  # 今日
        self.assertContains(response, "おしっこ 0 回、うんち 1 回")  # 昨日
