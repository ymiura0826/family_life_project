from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from account.models.family import Family

User = get_user_model()

class FamilyPasswordChangeTests(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            family_authentication_id="test_family",
            family_password=make_password("oldpassword")
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="userpass",
            family=self.family
        )
        self.url = reverse("family_pass_change")

    def test_change_password_successfully(self):
        self.client.login(username="testuser", password="userpass")
        response = self.client.post(self.url, {
            "current_password": "oldpassword",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        })
        self.assertRedirects(response, reverse("setting_complete"))
        self.family.refresh_from_db()
        self.assertTrue(self.family.family_password.startswith("pbkdf2_"))

    def test_wrong_current_password(self):
        self.client.login(username="testuser", password="userpass")
        response = self.client.post(self.url, {
            "current_password": "wrongpassword",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        })
        self.assertContains(response, "パスワードが違います")

    def test_mismatched_new_passwords(self):
        self.client.login(username="testuser", password="userpass")
        response = self.client.post(self.url, {
            "current_password": "oldpassword",
            "new_password": "newpass123",
            "confirm_password": "differentpass",
        })
        self.assertContains(response, "新しいパスワードが一致しません")

    def test_missing_all_fields(self):
        self.client.login(username="testuser", password="userpass")
        response = self.client.post(self.url, {})
        form = response.context['form']
        self.assertFormError(form, "current_password", "このフィールドは必須です。")
        form = response.context["form"]
        self.assertIn("このフィールドは必須です。", form.errors["new_password"])
        form = response.context["form"]
        self.assertIn("このフィールドは必須です。", form.errors["confirm_password"])

    def test_redirect_if_not_logged_in(self):
        login_url = reverse("login")
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_redirect_if_no_family(self):
        user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="userpass"
        )
        self.client.login(username="user2", password="userpass")
        response = self.client.get(self.url)
        reverse("family_register")
