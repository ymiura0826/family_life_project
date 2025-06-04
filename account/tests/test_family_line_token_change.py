from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from account.models.family import Family

User = get_user_model()

class FamilyLineTokenChangeTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.family = Family.objects.create(
            family_authentication_id="fam123",
            family_password=make_password(self.password),
            line_notify_id="original_token"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
            family=self.family
        )
        self.url = reverse("family_line_token_change")

    def test_get_form_authenticated(self):
        """ログインしてアクセスするとフォームが表示される"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "LINE通知トークン")

    def test_post_valid_data(self):
        """正しいパスワードと新トークンでトークン変更が成功"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "current_password": self.password,
            "new_token": "new_line_token"
        })
        self.assertRedirects(response, reverse("setting_complete"))
        self.family.refresh_from_db()
        self.assertEqual(self.family.line_notify_id, "new_line_token")

    def test_post_wrong_password(self):
        """パスワードが間違っているとバリデーションエラー"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "current_password": "wrongpass",
            "new_token": "new_token"
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], None, "パスワードが違います")
        self.family.refresh_from_db()
        self.assertEqual(self.family.line_notify_id, "original_token")

    def test_post_missing_token(self):
        """トークン未入力はバリデーションエラー"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "current_password": self.password,
            "new_token": ""
        })
        self.assertFormError(response.context["form"], "new_token", "このフィールドは必須です。")

    def test_post_missing_password(self):
        """パスワード未入力はバリデーションエラー"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "current_password": "",
            "new_token": "new_token"
        })
        self.assertFormError(response.context["form"], "current_password", "このフィールドは必須です。")

    def test_no_family_redirect(self):
        """family が紐づいていない場合は /family_select にリダイレクト"""
        self.user.family = None
        self.user.save()
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("family_select"))

    def test_redirect_if_not_logged_in(self):
        """未ログイン状態ではログイン画面にリダイレクトされる"""
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")
