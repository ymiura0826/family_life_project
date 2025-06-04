from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from account.models.family import Family

User = get_user_model()

class TopViewTests(TestCase):
    def setUp(self):
        self.url = reverse('top')
        self.dashboard_url = reverse('dashboard')
        self.family_select_url = reverse('family_select')

        self.family = Family.objects.create(
            family_authentication_id='testfamily',
            family_password='testpass123'
        )

        self.user_with_family = User.objects.create_user(
            username='withfamily',
            password='testpass',
            email='with@fam.com',
            family=self.family
        )

        self.user_without_family = User.objects.create_user(
            username='nofamily',
            password='testpass',
            email='no@fam.com',
            family=None
        )

    def test_top_view_anonymous(self):
        """未ログイン時は top.html を表示する"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'common/top.html')

    def test_top_view_authenticated_with_family(self):
        """ログイン済みかつ family あり → dashboard にリダイレクト"""
        self.client.login(username='withfamily', password='testpass')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.dashboard_url)

    def test_top_view_authenticated_without_family(self):
        """ログイン済みかつ family なし → family_select にリダイレクト"""
        self.client.login(username='nofamily', password='testpass')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.family_select_url)
