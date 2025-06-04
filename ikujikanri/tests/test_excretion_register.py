
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from account.models.family import Family
from account.models.child import Child
from account.models.notification_setting import NotificationSetting
from ikujikanri.models.excretion_record import ExcretionRecord
from ikujikanri.models.excretion_type import MstExcretionType
from account.models.sex import MstSex

User = get_user_model()


class ExcretionRecordRegisterTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sex = MstSex.objects.create(id=1, name='男の子', order_id=1)
        self.pee = MstExcretionType.objects.create(id=1, name='おしっこ', order_id=1)
        self.poo = MstExcretionType.objects.create(id=2, name='うんち', order_id=2)

        self.family = Family.objects.create(
            family_authentication_id='testfamily',
            family_password='testpass'
        )
        self.user = User.objects.create_user(username='testuser', password='pass', family=self.family)
        self.child = Child.objects.create(name='太郎', birth_date='2024-01-01', sex_id=1, family=self.family)
        NotificationSetting.objects.create(family=self.family, enable_notify_flag=False)

        self.client.login(username='testuser', password='pass')

    def test_register_pee_only(self):
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'excretion_type': str(self.pee.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExcretionRecord.objects.count(), 1)
        self.assertEqual(ExcretionRecord.objects.first().excretion_type, self.pee)

    def test_register_poo_only(self):
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'excretion_type': str(self.poo.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExcretionRecord.objects.count(), 1)
        self.assertEqual(ExcretionRecord.objects.first().excretion_type, self.poo)

    def test_register_both_types(self):
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'excretion_type': '99'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExcretionRecord.objects.count(), 2)

    def test_missing_action_at(self):
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'excretion_type': str(self.pee.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "このフィールドは必須です。")

    def test_missing_excretion_type(self):
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M')
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "排泄の種類を選択してください。")

    def test_nonexistent_child_id(self):
        url = reverse('excretion_register', kwargs={'child_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_other_family_child_access_forbidden(self):
        other_family = Family.objects.create(
            family_authentication_id='otherfam',
            family_password='otherpass'
        )
        other_child = Child.objects.create(name='次郎', birth_date='2024-01-01', sex_id=1, family=other_family)
        url = reverse('excretion_register', kwargs={'child_id': other_child.child_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_redirect_after_success(self):
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'excretion_type': str(self.pee.id)
        }
        # POSTで送信しているか？
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('ikujikanri_top'))


    def test_deleted_master_excretion_type_is_not_usable(self):
        self.pee.deleted_at = timezone.now()
        self.pee.save()
        url = reverse('excretion_register', kwargs={'child_id': self.child.child_id})
        data = {
            'action_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'excretion_type': str(self.pee.id)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
