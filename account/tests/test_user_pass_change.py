from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.shortcuts import resolve_url
from account.models.family import Family

User = get_user_model()

class UserPasswordChangeTests(TestCase):

    def setUp(self):
        self.family = Family.objects.create(
            family_authentication_id="testfamily",
            family_password="testpass123"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword123",
            family=self.family
        )
        self.url = reverse('user_pass_change')

    def test_password_change_success(self):
        self.client.login(username="testuser", password="oldpassword123")
        response = self.client.post(self.url, {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        self.assertRedirects(response, reverse('setting_complete'))
        self.user.refresh_from_db()
        self.assertTrue(check_password('newpassword456', self.user.password))

    def test_wrong_current_password(self):
        self.client.login(username="testuser", password="oldpassword123")
        response = self.client.post(self.url, {
            'current_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(form, None, "パスワードが違います")

    def test_mismatched_new_passwords(self):
        self.client.login(username="testuser", password="oldpassword123")
        response = self.client.post(self.url, {
            'current_password': 'oldpassword123',
            'new_password': 'abc123',
            'confirm_password': 'xyz456'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(form, None, "新しいパスワードが一致しません")

    def test_missing_all_fields(self):
        self.client.login(username="testuser", password="oldpassword123")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(form, 'current_password', 'このフィールドは必須です。')
        self.assertFormError(form, 'new_password', 'このフィールドは必須です。')
        self.assertFormError(form, 'confirm_password', 'このフィールドは必須です。')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        expected_url = resolve_url('login') + f'?next={self.url}'
        self.assertRedirects(response, expected_url)
