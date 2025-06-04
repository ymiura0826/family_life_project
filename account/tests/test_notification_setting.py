from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from account.models.family import Family
from account.models.notification_setting import NotificationSetting

User = get_user_model()

class NotificationSettingTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.family = Family.objects.create(
            family_authentication_id="fam123",
            family_password=make_password(self.password)
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
            family=self.family
        )
        self.url = reverse("notification_setting")

    def test_get_existing_notification_setting(self):
        """既存の通知設定がある場合に表示できる"""
        NotificationSetting.objects.create(
            family=self.family,
            enable_notify_flag=True
        )
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "育児管理通知を有効にする")

    def test_get_creates_notification_setting_if_not_exists(self):
        """通知設定が未作成でも自動作成されて表示される"""
        self.client.login(username="testuser", password=self.password)
        self.assertFalse(NotificationSetting.objects.filter(family=self.family).exists())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(NotificationSetting.objects.filter(family=self.family).exists())

    def test_post_enable_notify_true(self):
        """通知ONにして保存できる"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "enable_notify_flag": "on"
        })
        self.assertRedirects(response, "/setting/complete/")
        setting = NotificationSetting.objects.get(family=self.family)
        self.assertTrue(setting.enable_notify_flag)

    def test_post_enable_notify_false(self):
        """通知OFFにして保存できる"""
        NotificationSetting.objects.create(
            family=self.family,
            enable_notify_flag=True
        )
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {})  # チェックボックスが未送信 = False
        self.assertRedirects(response, "/setting/complete/")
        setting = NotificationSetting.objects.get(family=self.family)
        self.assertFalse(setting.enable_notify_flag)

    def test_redirect_if_not_logged_in(self):
        """未ログイン時はログイン画面にリダイレクトされる"""
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_redirect_if_no_family(self):
        """ログイン済みでもfamilyが未設定ならfamily_selectにリダイレクトされる"""
        self.user.family = None
        self.user.save()
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("family_select"))
