from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family

User = get_user_model()

class FamilySelectViewTests(TestCase):
    def setUp(self):
        self.url = reverse("family_select")
        self.user_with_family = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass"
        )
        self.user_without_family = User.objects.create_user(
            username="user2", 
            email="user2@example.com", 
            password="testpass"
        )
        self.family = Family.objects.create(family_authentication_id="test123", family_password="dummy")
        self.user_with_family.family = self.family
        self.user_with_family.save()

    def test_redirect_if_not_logged_in(self):
        """ログインしていない場合はログイン画面にリダイレクトされる"""
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_display_if_logged_in_without_family(self):
        """ログイン済みで family が未設定なら表示される"""
        self.client.login(username="user2", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/family_select.html")

    def test_redirect_if_logged_in_with_family(self):
        """ログイン済みで family 設定済みなら dashboard にリダイレクト"""
        self.client.login(username="user1", password="testpass")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))
