from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from account.models.family import Family
from account.models.child import Child
from account.models.sex import MstSex
from ikujikanri.models.milk_record import MilkRecord
from ikujikanri.models.milk_type import MstMilkType

User = get_user_model()

class MilkDetailViewTests(TestCase):
    def setUp(self):
        self.sex = MstSex.objects.create(id=1, name='男の子', order_id=1)
        self.milk_type_breast = MstMilkType.objects.create(id=1, name='母乳', order_id=1)
        self.milk_type_powder = MstMilkType.objects.create(id=2, name='粉ミルク', order_id=2)

        self.family = Family.objects.create(family_authentication_id="fam001", family_password="password")
        self.user = User.objects.create_user(username="testuser", password="testpass", family=self.family)
        self.client.login(username="testuser", password="testpass")

        self.child = Child.objects.create(name="テスト太郎", birth_date="2020-01-01", sex=self.sex, family=self.family)
        self.record = MilkRecord.objects.create(
            child=self.child,
            milk_type=self.milk_type_powder,
            amount=100,
            action_at=timezone.now()
        )

        self.other_family = Family.objects.create(family_authentication_id="fam002", family_password="password")
        self.other_child = Child.objects.create(name="他人の子", birth_date="2020-01-01", sex=self.sex, family=self.other_family)
        self.other_record = MilkRecord.objects.create(
            child=self.other_child,
            milk_type=self.milk_type_powder,
            amount=100,
            action_at=timezone.now()
        )

    def get_detail_url(self, pk):
        return reverse("milk_detail", kwargs={"pk": pk})

    def test_can_view_own_record(self):
        res = self.client.get(self.get_detail_url(self.record.pk))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "ミルクの種類")

    def test_cannot_view_other_family_record(self):
        res = self.client.get(self.get_detail_url(self.other_record.pk))
        self.assertEqual(res.status_code, 404)

    def test_cannot_view_deleted_record(self):
        self.record.deleted_at = timezone.now()
        self.record.save()
        res = self.client.get(self.get_detail_url(self.record.pk))
        self.assertEqual(res.status_code, 404)

    def test_update_breast_milk_valid(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_breast.id,
            "amount": "",
            "left_breast_minutes": 5,
            "right_breast_minutes": "",
            "notify_flag": False,
            "next_milk_at": "",
        }
        res = self.client.post(self.get_detail_url(self.record.pk), data)
        self.assertRedirects(res, reverse("milk_list", kwargs={"child_id": self.child.child_id}))
        self.record.refresh_from_db()
        self.assertEqual(self.record.left_breast_minutes, 5)

    def test_update_powder_milk_valid(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "amount": 150,
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "notify_flag": False,
            "next_milk_at": "",
        }
        res = self.client.post(self.get_detail_url(self.record.pk), data)
        self.assertRedirects(res, reverse("milk_list", kwargs={"child_id": self.child.child_id}))
        self.record.refresh_from_db()
        self.assertEqual(self.record.amount, 150)

    def test_validation_error_breast_milk_no_minutes(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_breast.id,
            "amount": "",
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "notify_flag": False,
            "next_milk_at": "",
        }
        res = self.client.post(self.get_detail_url(self.record.pk), data)
        self.assertContains(res, "母乳の場合は左右いずれかの授乳時間を入力してください。")

    def test_validation_error_powder_milk_no_amount(self):
        data = {
            "action_at": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "milk_type": self.milk_type_powder.id,
            "amount": "",
            "left_breast_minutes": "",
            "right_breast_minutes": "",
            "notify_flag": False,
            "next_milk_at": "",
        }
        res = self.client.post(self.get_detail_url(self.record.pk), data)
        self.assertContains(res, "粉ミルクまたは搾乳の場合は量を入力してください。")

    def test_post_delete_sets_deleted_at(self):
        res = self.client.post(self.get_detail_url(self.record.pk), {"delete": "1"})
        self.assertRedirects(res, reverse("milk_list", kwargs={"child_id": self.child.child_id}))
        self.record.refresh_from_db()
        self.assertIsNotNone(self.record.deleted_at)

    def test_delete_other_family_record_raises_404(self):
        res = self.client.post(self.get_detail_url(self.other_record.pk), {"delete": "1"})
        self.assertEqual(res.status_code, 404)

    def test_delete_already_deleted_record_raises_404(self):
        self.record.deleted_at = timezone.now()
        self.record.save()
        res = self.client.post(self.get_detail_url(self.record.pk), {"delete": "1"})
        self.assertEqual(res.status_code, 404)
