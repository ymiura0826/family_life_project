# account/tests/test_login.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family

User = get_user_model()


class LoginViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
        self.family_select_url = reverse('family_select')

        self.family = Family.objects.create(
            family_authentication_id="testfamily",
            family_password="testpass123"
        )

        self.valid_username = "validuser"
        self.valid_password = "password123"

        self.user_with_family = User.objects.create_user(
            username=self.valid_username,
            email="with@family.com",
            password=self.valid_password,
            family=self.family
        )

        self.user_without_family = User.objects.create_user(
            username="nofamilyuser",
            email="no@family.com",
            password="password123",
            family=None
        )

    def test_login_success_with_family(self):
        response = self.client.post(self.login_url, {
            'username': self.valid_username,
            'password': self.valid_password
        })
        self.assertRedirects(response, self.dashboard_url)

    def test_login_success_without_family(self):
        response = self.client.post(self.login_url, {
            'username': "nofamilyuser",
            'password': "password123"
        })
        self.assertRedirects(response, self.family_select_url)

    def test_login_missing_username(self):
        response = self.client.post(self.login_url, {
            'username': '',
            'password': 'password123'
        })
        form = response.context['form']
        self.assertFormError(form, 'username', 'このフィールドは必須です。')

    def test_login_missing_password(self):
        response = self.client.post(self.login_url, {
            'username': self.valid_username,
            'password': ''
        })
        form = response.context['form']
        self.assertFormError(form, 'password', 'このフィールドは必須です。')

    def test_login_both_fields_missing(self):
        response = self.client.post(self.login_url, {
            'username': '',
            'password': ''
        })
        form = response.context['form']
        self.assertFormError(form, 'username', 'このフィールドは必須です。')
        self.assertFormError(form, 'password', 'このフィールドは必須です。')

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {
            'username': self.valid_username,
            'password': 'wrongpassword'
        })
        self.assertContains(response, 'IDもしくはパスが間違っています')

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'unknownuser',
            'password': 'password123'
        })
        self.assertContains(response, 'IDもしくはパスが間違っています')

    def test_authenticated_user_redirects(self):
        response = self.client.post(self.login_url, {
            'username': self.valid_username,
            'password': self.valid_password
        })

        self.assertRedirects(response, self.dashboard_url)