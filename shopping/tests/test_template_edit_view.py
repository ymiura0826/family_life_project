from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from shopping.models.shopping_item_template import ShoppingItemTemplate
from shopping.models.shopping_item_category import MstShoppingItemCategory
from account.models.family import Family

User = get_user_model()

class ShoppingTemplateEditViewTests(TestCase):
    def setUp(self):
        # 家族を2つ用意
        self.family1 = Family.objects.create(
            family_authentication_id='fam1', family_password='pass'
        )
        self.family2 = Family.objects.create(
            family_authentication_id='fam2', family_password='pass'
        )
        # ユーザー作成
        self.user1 = User.objects.create_user(
            username='user1', email='u1@example.com', password='pass', family=self.family1
        )
        self.user_no_family = User.objects.create_user(
            username='user2', email='u2@example.com', password='pass'
        )
        # カテゴリ作成
        self.cat1 = MstShoppingItemCategory.objects.create(name='食品', order_id=1)
        self.cat2 = MstShoppingItemCategory.objects.create(name='日用品', order_id=2)
        # 既存テンプレートを2件作成
        self.tpl1 = ShoppingItemTemplate.objects.create(
            shopping_item_category=self.cat1,
            item_name='卵', memo='6個',
            family=self.family1, order_id=0
        )
        self.tpl2 = ShoppingItemTemplate.objects.create(
            shopping_item_category=self.cat2,
            item_name='牛乳', memo='',
            family=self.family1, order_id=1
        )

    def test_get_not_logged_in(self):
        url = reverse('shopping_template_edit', args=[self.family1.family_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_get_no_family(self):
        self.client.force_login(self.user_no_family)
        url = reverse('shopping_template_edit', args=[self.family1.family_id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('family_select'))

    def test_get_family_id_mismatch(self):
        self.client.force_login(self.user1)
        wrong_url = reverse('shopping_template_edit', args=[self.family2.family_id])
        response = self.client.get(wrong_url)
        expected = reverse('shopping_template_edit', args=[self.family1.family_id])
        self.assertRedirects(response, expected)

    def test_get_success_context(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_template_edit', args=[self.family1.family_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopping/template_edit.html')
        formset = response.context['formset']
        # 2 件のフォームがある
        self.assertEqual(len(formset.forms), 2)
        self.assertEqual(response.context['family_id'], self.family1.family_id)

    def test_get_no_templates(self):
        # family2 にテンプレートなし
        self.client.force_login(self.user1)
        # 清空 family1 のテンプレート
        ShoppingItemTemplate.objects.filter(family=self.family1).delete()
        url = reverse('shopping_template_edit', args=[self.family1.family_id])
        response = self.client.get(url)
        formset = response.context['formset']
        self.assertEqual(len(formset.forms), 0)

    def test_post_update_and_delete_and_add(self):
        """既存更新・削除・新規追加が同時に動作する"""
        self.client.force_login(self.user1)
        url = reverse('shopping_template_edit', args=[self.family1.family_id])
        # 準備：3件目の新規追加用データ
        total = 3
        data = {
            'form-TOTAL_FORMS': str(total),
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
        }
        # 0: 更新
        data.update({
            'form-0-id': str(self.tpl1.id),
            'form-0-order_id': '0',
            'form-0-shopping_item_category': str(self.cat2.id),
            'form-0-item_name': '卵改',
            'form-0-memo': '9個',
            'form-0-DELETE': '',
        })
        # 1: 削除
        data.update({
            'form-1-id': str(self.tpl2.id),
            'form-1-order_id': '1',
            'form-1-shopping_item_category': str(self.cat2.id),
            'form-1-item_name': '牛乳',
            'form-1-memo': '',
            'form-1-DELETE': 'on',
        })
        # 2: 新規追加
        data.update({
            'form-2-id': '',
            'form-2-order_id': '2',
            'form-2-shopping_item_category': str(self.cat1.id),
            'form-2-item_name': 'パン',
            'form-2-memo': '2斤',
            'form-2-DELETE': '',
        })

        response = self.client.post(url, data)
        # リダイレクト
        self.assertRedirects(response, url)

        # 更新された tpl1
        self.tpl1.refresh_from_db()
        self.assertEqual(self.tpl1.shopping_item_category, self.cat2)
        self.assertEqual(self.tpl1.item_name, '卵改')
        self.assertEqual(self.tpl1.memo, '9個')
        self.assertIsNone(self.tpl1.deleted_at)
        # tpl2 は論理削除
        self.tpl2.refresh_from_db()
        self.assertIsNotNone(self.tpl2.deleted_at)
        # 新規追加されたレコード確認
        new_tpl = ShoppingItemTemplate.objects.filter(family=self.family1, item_name='パン').first()
        self.assertIsNotNone(new_tpl)
        self.assertEqual(new_tpl.shopping_item_category, self.cat1)
        self.assertEqual(new_tpl.memo, '2斤')

    def test_post_validation_error(self):
        """必須項目欠損で再描画、DB変更なし"""
        self.client.force_login(self.user1)
        url = reverse('shopping_template_edit', args=[self.family1.family_id])
        total = 2
        data = {
            'form-TOTAL_FORMS': str(total),
            'form-INITIAL_FORMS': str(total),
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            # 両方とも item_name 欠損
            'form-0-id': str(self.tpl1.id),
            'form-0-order_id': '0',
            'form-0-shopping_item_category': str(self.cat1.id),
            'form-0-item_name': '',
            'form-0-memo': '',
            'form-0-DELETE': '',
            'form-1-id': str(self.tpl2.id),
            'form-1-order_id': '1',
            'form-1-shopping_item_category': str(self.cat2.id),
            'form-1-item_name': '',
            'form-1-memo': '',
            'form-1-DELETE': '',
        }
        response = self.client.post(url, data)
        # 再描画
        self.assertEqual(response.status_code, 200)
        formset = response.context['formset']
        self.assertTrue(formset.forms[0].errors)
        self.assertTrue(formset.forms[1].errors)
        # DB は未変更
        self.tpl1.refresh_from_db()
        self.assertEqual(self.tpl1.item_name, '卵')

    def test_post_family_id_mismatch(self):
        """URL family_id 不一致でリダイレクト、DB変更なし"""
        self.client.force_login(self.user1)
        wrong_url = reverse('shopping_template_edit', args=[self.family2.family_id])
        # minimal management form
        data = {'form-TOTAL_FORMS': '0', 'form-INITIAL_FORMS': '0', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000'}
        response = self.client.post(wrong_url, data)
        expected = reverse('shopping_template_edit', args=[self.family1.family_id])
        self.assertRedirects(response, expected)
        # DB 未変更
        self.tpl1.refresh_from_db()
        self.assertIsNone(self.tpl1.deleted_at)
