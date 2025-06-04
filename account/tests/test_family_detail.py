from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from account.models.family import Family
from account.models.child import Child
from datetime import date

User = get_user_model()

class FamilyDetailViewTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.family = Family.objects.create(
            family_authentication_id="fam123",
            family_password=make_password(self.password)
        )
        self.other_family = Family.objects.create(
            family_authentication_id="fam999",
            family_password=make_password("otherpass")
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
            family=self.family
        )
        self.url = reverse("family_detail", kwargs={"pk": self.family.family_id})

    def test_get_family_detail_success(self):
        """自分のfamily_idでアクセスできる"""
        self.client.login(username="testuser", password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.family.family_authentication_id)
        self.assertIn("family", response.context)
        self.assertEqual(response.context["family"], self.family)

    def test_redirect_if_family_id_not_match(self):
        """他人のfamily_idでアクセスするとdashboardにリダイレクト"""
        self.client.login(username="testuser", password=self.password)
        url = reverse("family_detail", kwargs={"pk": self.other_family.family_id})
        response = self.client.get(url)
        self.assertRedirects(response, "/dashboard/")

    def test_redirect_if_no_family_set(self):
        """ログイン済だがfamilyがNoneのときはfamily_selectにリダイレクト"""
        self.user.family = None
        self.user.save()
        self.client.login(username="testuser", password=self.password)
        url = reverse("family_detail", kwargs={"pk": self.family.family_id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("family_select"))

    def test_redirect_if_not_logged_in(self):
        """未ログイン状態ならログインページにリダイレクト"""
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_active_children_in_context(self):
        """削除されていない子どもだけがcontextに含まれる"""
        self.client.login(username="testuser", password=self.password)
        # 有効な子
        active_child = Child.objects.create(
            name="Taro",
            birth_date=date(2022, 1, 1),
            family=self.family
        )
        # 論理削除された子
        deleted_child = Child.objects.create(
            name="Jiro",
            birth_date=date(2020, 1, 1),
            family=self.family,
            deleted_at=date.today()
        )
        response = self.client.get(self.url)
        children = response.context["active_children"]
        self.assertIn(active_child, children)
        self.assertNotIn(deleted_child, children)
