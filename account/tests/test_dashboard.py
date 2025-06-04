# account/tests/test_dashboard.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            family_authentication_id="fam001",
            family_password="dummy_pw",
            line_notify_id="dummy_line"
        )
        self.user_with_family = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
            family=self.family
        )
        self.user_no_family = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
            family=None
        )
        self.url = reverse("dashboard")

    def test_redirect_if_not_logged_in(self):
        """ログインしていない場合はログインページにリダイレクトされる"""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_redirect_if_logged_in_but_no_family(self):
        """ログイン済みでも family が未設定なら /register/family/ にリダイレクトされる"""
        self.client.login(username="user2", password="testpass123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("family_select"))

    def test_dashboard_display_for_authenticated_user_with_family(self):
        """ログイン済みかつ family 設定済みの場合、ダッシュボードが表示される"""
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "common/dashboard.html")
