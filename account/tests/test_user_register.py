from django.test import TestCase
from django.urls import reverse
from account.models.user import CustomUser

class TestUserRegisterView(TestCase):
    def setUp(self):
        self.url = reverse('user_register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        }
        # 重複チェック用ユーザー
        CustomUser.objects.create_user(
            username='existinguser',
            email='duplicate@example.com',
            password='password123'
        )

    def test_register_success(self):
        """正常に登録でき、family_select にリダイレクトされる"""
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('family_select'))
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())

    def test_register_duplicate_email(self):
        """登録済みメールアドレスを使うとエラーになる"""
        data = self.valid_data.copy()
        data['email'] = 'duplicate@example.com'
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'メールアドレスは登録済みです')

    def test_register_missing_username(self):
        """ユーザー名未入力でエラーメッセージが出る"""
        data = self.valid_data.copy()
        data['username'] = ''
        response = self.client.post(self.url, data)
        form = response.context["form"]
        self.assertFormError(form, 'username', 'このフィールドは必須です。')

    def test_register_missing_email(self):
        """メールアドレス未入力でエラーメッセージが出る"""
        data = self.valid_data.copy()
        data['email'] = ''
        response = self.client.post(self.url, data)
        form = response.context["form"]
        self.assertFormError(form, 'email', 'このフィールドは必須です。')

    def test_register_password_mismatch(self):
        """パスワードが一致しないとエラーメッセージが出る"""
        data = self.valid_data.copy()
        data['password2'] = 'differentpassword'
        response = self.client.post(self.url, data)
        self.assertContains(response, '確認用パスワードが一致しません')
