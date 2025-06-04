from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from account.models.family import Family
from account.models.child import Child
from account.models.sex import MstSex
from ikujikanri.models.excretion_record import ExcretionRecord
from ikujikanri.models.excretion_type import MstExcretionType

User = get_user_model()

class ExcretionRecordListViewTests(TestCase):
    def setUp(self):
        self.sex = MstSex.objects.create(id=1, name='男の子', order_id=1)
        self.ex_type = MstExcretionType.objects.create(id=1, name='おしっこ', order_id=1)

        self.family = Family.objects.create(family_authentication_id="fam001", family_password="password")
        self.user = User.objects.create_user(username="testuser", password="testpass", family=self.family)
        self.client.login(username="testuser", password="testpass")

        self.child = Child.objects.create(name="テスト太郎", birth_date="2020-01-01", sex=self.sex, family=self.family)
        self.other_family = Family.objects.create(family_authentication_id="fam002", family_password="password")
        self.other_child = Child.objects.create(name="他人の子", birth_date="2020-01-01", sex=self.sex, family=self.other_family)

    def test_records_exist_within_one_week(self):
        ExcretionRecord.objects.create(
            child=self.child,
            excretion_type=self.ex_type,
            memo="正常です",
            action_at=timezone.now()
        )
        url = reverse("excretion_list", kwargs={"child_id": self.child.child_id})
        response = self.client.get(url)
        self.assertContains(response, "正常です")
        self.assertContains(response, "おしっこ")

    def test_no_records(self):
        url = reverse("excretion_list", kwargs={"child_id": self.child.child_id})
        response = self.client.get(url)
        self.assertContains(response, "記録がありません。")

    def test_access_other_family_child(self):
        url = reverse("excretion_list", kwargs={"child_id": self.other_child.child_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_deleted_record_not_shown(self):
        ExcretionRecord.objects.create(
            child=self.child,
            excretion_type=self.ex_type,
            memo="削除された記録",
            action_at=timezone.now(),
            deleted_at=timezone.now()
        )
        url = reverse("excretion_list", kwargs={"child_id": self.child.child_id})
        response = self.client.get(url)
        self.assertContains(response, "記録がありません。")

    def test_old_record_not_shown(self):
        old_date = timezone.now() - timedelta(days=8)
        ExcretionRecord.objects.create(
            child=self.child,
            excretion_type=self.ex_type,
            memo="古い記録",
            action_at=old_date
        )
        url = reverse("excretion_list", kwargs={"child_id": self.child.child_id})
        response = self.client.get(url)
        self.assertContains(response, "記録がありません。")

    def test_record_with_empty_memo(self):
        ExcretionRecord.objects.create(
            child=self.child,
            excretion_type=self.ex_type,
            memo="",
            action_at=timezone.now()
        )
        url = reverse("excretion_list", kwargs={"child_id": self.child.child_id})
        response = self.client.get(url)
        self.assertContains(response, "おしっこ")
        self.assertNotContains(response, "メモ：")

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        url = reverse("excretion_list", kwargs={"child_id": self.child.child_id})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)
