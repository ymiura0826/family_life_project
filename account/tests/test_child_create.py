from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from account.models.family import Family
from account.models.child import Child
from account.models.sex import MstSex

User = get_user_model()

class ChildCreateViewTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.family = Family.objects.create(
            family_authentication_id="fam123",
            family_password=make_password(self.password)
        )
        self.sex = MstSex.objects.create(name="男の子", order_id=1)
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
            family=self.family
        )
        self.url = reverse("child_create")

    def test_create_child_success_all_fields(self):
        """全項目入力で正常登録"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "name": "太郎",
            "birth_date": "2023-01-01",
            "sex": self.sex.pk
        })
        self.assertRedirects(response, reverse("setting_complete"))
        self.assertEqual(Child.objects.count(), 1)
        child = Child.objects.first()
        self.assertEqual(child.name, "太郎")
        self.assertEqual(child.family, self.family)
        self.assertEqual(child.sex, self.sex)

    def test_create_child_without_sex(self):
        """性別なしでも登録できる"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "name": "花子",
            "birth_date": "2022-12-12",
            "sex": ""
        })
        self.assertRedirects(response, reverse("setting_complete"))
        self.assertEqual(Child.objects.count(), 1)
        self.assertIsNone(Child.objects.first().sex)

    def test_create_child_missing_name(self):
        """名前が未入力でバリデーションエラー"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "name": "",
            "birth_date": "2023-01-01",
            "sex": self.sex.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "このフィールドは必須です。")
        self.assertEqual(Child.objects.count(), 0)

    def test_create_child_missing_birth_date(self):
        """誕生日が未入力でバリデーションエラー"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.url, {
            "name": "次郎",
            "birth_date": "",
            "sex": self.sex.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "birth_date", "このフィールドは必須です。")
        self.assertEqual(Child.objects.count(), 0)

    def test_redirect_if_not_logged_in(self):
        """未ログインでアクセスするとログイン画面にリダイレクト"""
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_redirect_if_post_not_logged_in(self):
        """未ログインでPOSTしてもログイン画面にリダイレクト"""
        response = self.client.post(self.url, {
            "name": "匿名",
            "birth_date": "2023-01-01",
            "sex": self.sex.pk
        })
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")
        self.assertEqual(Child.objects.count(), 0)

    def test_redirect_if_no_family_set(self):
        """ログイン済みでもfamilyがない場合はfamily_selectにリダイレクト"""
        self.user.family = None
        self.user.save()
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("family_select"))
