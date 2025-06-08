from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from shopping.models.shopping_item import ShoppingItem
from shopping.models.shopping_item_category import MstShoppingItemCategory
from account.models.family import Family

User = get_user_model()

class ShoppingItemUpdateViewTests(TestCase):
    def setUp(self):
        # 家族を2つ作成
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
        # アイテム作成
        self.item1 = ShoppingItem.objects.create(
            shopping_item_category=self.cat1,
            item_name='卵', memo='6個',
            family=self.family1, user=self.user1, completion_flag=False
        )
        # 論理削除済みアイテム
        self.deleted_item = ShoppingItem.objects.create(
            shopping_item_category=self.cat1,
            item_name='牛乳', memo='',
            family=self.family1, user=self.user1, completion_flag=False
        )
        self.deleted_item.deleted_at = timezone.now()
        self.deleted_item.save(update_fields=['deleted_at'])

    def test_get_not_logged_in(self):
        url = reverse('shopping_item_edit', args=[self.item1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_get_no_family(self):
        self.client.force_login(self.user_no_family)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('family_select'))

    def test_get_invalid_pk_404(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_other_family_404(self):
        other_user = User.objects.create_user(
            username='user3', email='u3@example.com', password='pass', family=self.family2
        )
        self.client.force_login(other_user)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_deleted_item_404(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[self.deleted_item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_success_and_context(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopping/item_edit.html')
        form = response.context['form']
        self.assertEqual(form.initial['shopping_item_category'], self.cat1.id)
        self.assertEqual(form.initial['item_name'], self.item1.item_name)
        self.assertEqual(form.initial['memo'], self.item1.memo)

    def test_post_save_valid(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        data = {
            'shopping_item_category': str(self.cat2.id),
            'item_name': 'パン',
            'memo': '2斤'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('shopping_top'))
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.shopping_item_category, self.cat2)
        self.assertEqual(self.item1.item_name, 'パン')
        self.assertEqual(self.item1.memo, '2斤')
        self.assertIsNone(self.item1.deleted_at)

    def test_post_save_invalid(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        data = {'shopping_item_category': '', 'item_name': '', 'memo': ''}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('shopping_item_category', form.errors)
        self.assertIn('item_name', form.errors)
        # DB は未変更
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.shopping_item_category, self.cat1)

    def test_post_delete_valid(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        response = self.client.post(url, {'action': 'delete'})
        self.assertRedirects(response, reverse('shopping_top'))
        self.item1.refresh_from_db()
        self.assertIsNotNone(self.item1.deleted_at)

    def test_post_delete_invalid_pk_404(self):
        self.client.force_login(self.user1)
        url = reverse('shopping_item_edit', args=[9999])
        response = self.client.post(url, {'action': 'delete'})
        self.assertEqual(response.status_code, 404)

    def test_post_delete_other_family_404(self):
        other_user = User.objects.create_user(
            username='user4', email='u4@example.com', password='pass', family=self.family2
        )
        self.client.force_login(other_user)
        url = reverse('shopping_item_edit', args=[self.item1.id])
        response = self.client.post(url, {'action': 'delete'})
        self.assertEqual(response.status_code, 404)
