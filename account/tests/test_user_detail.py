from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family

User = get_user_model()

class UserDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')
        self.family_select_url = reverse('family_select')

        self.family = Family.objects.create(
            family_authentication_id='testid',
            family_password='testpass',
            line_notify_id='dummy_notify_id'
        )
        self.user1 = User.objects.create_user(username='user1', password='pass1', email='user1@example.com', family=self.family)
        self.user2 = User.objects.create_user(username='user2', password='pass2', email='user2@example.com', family=self.family)
        self.user3 = User.objects.create_user(username='user3', password='pass3', email='user3@example.com')  # familyなし

        self.detail_url_user1 = reverse('user_detail', kwargs={'pk': self.user1.id})
        self.detail_url_user2 = reverse('user_detail', kwargs={'pk': self.user2.id})
        self.detail_url_user3 = reverse('user_detail', kwargs={'pk': self.user3.id})

    def test_redirect_if_not_logged_in(self):
        """未ログイン → ログインページへ"""
        response = self.client.get(self.detail_url_user1)
        expected_url = f"{self.login_url}?next={self.detail_url_user1}"
        self.assertRedirects(response, expected_url)

    def test_redirect_if_other_user(self):
        """ログイン済みだが他人のページにアクセス → ダッシュボードにリダイレクト"""
        logged_in = self.client.login(username="user1", password="pass1")
        self.assertTrue(logged_in, "ログインに失敗しました")
        response = self.client.get(self.detail_url_user2)
        self.assertRedirects(response, reverse('dashboard'))

    def test_display_own_user_detail(self):
        """ログイン済み、自分のID指定 → 正常に表示"""
        logged_in = self.client.login(username="user1", password="pass1")
        self.assertTrue(logged_in, "ログインに失敗しました")
        response = self.client.get(self.detail_url_user1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/user_detail.html")
        self.assertEqual(response.context["user_obj"], self.user1)

    def test_redirect_if_no_family(self):
        """ログイン済みだがfamily未登録 → family_selectにリダイレクト"""
        self.user3.family = None
        self.user3.save()
        logged_in = self.client.login(username="user3", password="pass3")
        self.assertTrue(logged_in, "ログインに失敗しました")
        response = self.client.get(self.detail_url_user3)
        self.assertRedirects(response, reverse("family_select"))
