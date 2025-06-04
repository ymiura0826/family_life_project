# account/tests/test_logout.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family

User = get_user_model()

class LogoutViewTests(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            family_authentication_id="testfamily",
            family_password="testpass123"
        )
        self.user = User.objects.create_user(
            username="logoutuser",
            email="logout@user.com",
            password="password123",
            family=self.family
        )
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.dashboard_url = reverse('dashboard')

    def test_logout_successfully(self):
        # ログインしてログアウト
        self.client.login(username="logoutuser", password="password123")
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, '/')  # 例：ログアウト後ログイン画面に戻る

        # ログアウト後にダッシュボードにアクセス→ログインページに飛ばされる
        response_after = self.client.get(self.dashboard_url)
        self.assertRedirects(response_after, f"{self.login_url}?next={self.dashboard_url}")

    def test_logout_when_not_logged_in(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, '/')  # 未ログインでもログアウトURLは叩けるがログイン画面に飛ぶ

    def test_session_is_cleared_after_logout(self):
        self.client.login(username="logoutuser", password="password123")
        self.client.get(self.logout_url)
        # ログアウト後にセッション内にユーザー情報がないことを確認
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.dashboard_url}")
