import datetime
from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family
from account.models.child import Child
from ikujikanri.models.excretion_record import ExcretionRecord
from ikujikanri.models.excretion_type import MstExcretionType
from account.models.sex import MstSex

User = get_user_model()

class ExcretionRecordDetailTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.sex = MstSex.objects.create(id=1, name='男の子', order_id=1)
        self.pee = MstExcretionType.objects.create(name='おしっこ', order_id=1)
        self.poo = MstExcretionType.objects.create(name='うんち', order_id=2)

        self.family = Family.objects.create(family_authentication_id='testfam', family_password='pass')
        self.user = User.objects.create_user(username='testuser', password='pass', family=self.family)
        self.child = Child.objects.create(name='太郎', birth_date='2024-01-01', sex=self.sex, family=self.family)

        self.record = ExcretionRecord.objects.create(
            child=self.child,
            action_at=timezone.now(),
            excretion_type=self.pee,
            memo='初回記録'
        )

        self.client.login(username='testuser', password='pass')

    def test_get_detail_page(self):
        url = reverse('excretion_detail', kwargs={'excretion_record_id': self.record.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "排泄の種類")

    def test_update_success(self):
        url = reverse('excretion_detail', kwargs={'excretion_record_id': self.record.id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'excretion_type': self.poo.id,
            'memo': '更新済み'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('excretion_list', kwargs={'child_id': self.child.child_id}))
        self.record.refresh_from_db()
        self.assertEqual(self.record.excretion_type, self.poo)
        self.assertEqual(self.record.memo, '更新済み')

    def test_update_missing_action_at(self):
        url = reverse('excretion_detail', kwargs={'excretion_record_id': self.record.id})
        data = {
            'action_at': '',  # 明示的に空にする
            'excretion_type': self.pee.id,
            'memo': 'メモだけ'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "このフィールドは必須です。")

    def test_update_missing_action_at(self):
        url = reverse('excretion_detail', kwargs={'excretion_record_id': self.record.id})
        data = {
            'action_at': '',  # 明示的に空
            'excretion_type': self.pee.id,
            'memo': 'メモだけ'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "実施日時を入力してください。")


    def test_delete_sets_deleted_at(self):
        url = reverse('excretion_detail', kwargs={'excretion_record_id': self.record.id})
        response = self.client.post(url, {'delete': '1'})
        self.assertRedirects(response, reverse('excretion_list', kwargs={'child_id': self.child.child_id}))
        self.record.refresh_from_db()
        self.assertIsNotNone(self.record.deleted_at)

    def test_access_deleted_record_returns_404(self):
        self.record.deleted_at = timezone.now()
        self.record.save()
        url = reverse('excretion_detail', kwargs={'excretion_record_id': self.record.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_access_other_family_record_forbidden(self):
        other_family = Family.objects.create(family_authentication_id='otherfam', family_password='otherpass')
        other_child = Child.objects.create(name='次郎', birth_date='2024-01-01', sex=self.sex, family=other_family)
        other_record = ExcretionRecord.objects.create(
            child=other_child,
            action_at=timezone.now(),
            excretion_type=self.pee
        )
        url = reverse('excretion_detail', kwargs={'excretion_record_id': other_record.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
