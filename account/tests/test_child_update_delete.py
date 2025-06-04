from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from account.models.family import Family
from account.models.child import Child
from account.models.sex import MstSex

User = get_user_model()

class ChildUpdateDeleteTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.family = Family.objects.create(
            family_authentication_id="fam123",
            family_password=make_password(self.password)
        )
        self.other_family = Family.objects.create(
            family_authentication_id="fam999",
            family_password=make_password("pass999")
        )
        self.sex = MstSex.objects.create(name="女の子", order_id=1)
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
            family=self.family
        )
        self.child = Child.objects.create(
            name="テスト子",
            birth_date="2022-01-01",
            sex=self.sex,
            family=self.family
        )
        self.other_child = Child.objects.create(
            name="他人の子",
            birth_date="2021-01-01",
            sex=self.sex,
            family=self.other_family
        )
        self.update_url = reverse("child_update", kwargs={"pk": self.child.pk})
        self.delete_url = reverse("child_delete", kwargs={"pk": self.child.pk})

    def test_get_update_view_success(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "名前")

    def test_post_update_success(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.update_url, {
            "name": "更新後名前",
            "birth_date": "2023-03-03",
            "sex": self.sex.pk
        })
        self.assertRedirects(response, reverse("setting_complete"))
        self.child.refresh_from_db()
        self.assertEqual(self.child.name, "更新後名前")

    def test_post_update_without_sex(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.update_url, {
            "name": "性別なし",
            "birth_date": "2023-01-01",
            "sex": ""
        })
        self.assertRedirects(response, reverse("setting_complete"))
        self.child.refresh_from_db()
        self.assertIsNone(self.child.sex)

    def test_post_update_missing_name(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.update_url, {
            "name": "",
            "birth_date": "2023-01-01",
            "sex": self.sex.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "このフィールドは必須です。")

    def test_post_update_missing_birth_date(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.update_url, {
            "name": "名前あり",
            "birth_date": "",
            "sex": self.sex.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "birth_date", "このフィールドは必須です。")

    def test_update_redirect_if_not_logged_in(self):
        response = self.client.get(self.update_url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.update_url}")

    def test_update_404_if_other_family(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="pass",
            family=self.other_family
        )
        self.client.login(username="otheruser", password="pass")
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 404)

    def test_post_delete_success(self):
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("setting_complete"))
        self.child.refresh_from_db()
        self.assertIsNotNone(self.child.deleted_at)

    def test_post_delete_other_family_404(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="pass",
            family=self.other_family
        )
        self.client.login(username="otheruser", password="pass")
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)

    def test_post_delete_not_logged_in_redirect(self):
        response = self.client.post(self.delete_url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.delete_url}")

    def test_post_delete_no_family_redirect(self):
        self.user.family = None
        self.user.save()
        self.client.login(username="testuser", password=self.password)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse("family_select"))
