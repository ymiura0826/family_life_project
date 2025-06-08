from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from shopping.models.shopping_item import ShoppingItem
from shopping.models.shopping_item_template import ShoppingItemTemplate
from shopping.models.shopping_item_category import MstShoppingItemCategory
from account.models.family import Family
from notification.models.notify_schedule import NotifySchedule
from notification.models.notify_type import MstNotifyType
from notification.models.notify_method import MstNotifyMethod
from shopping.forms import ShoppingItemRowForm

User = get_user_model()

class ShoppingTopViewTests(TestCase):
    def setUp(self):
        # 家族・ユーザーを作成
        self.family = Family.objects.create(
            family_authentication_id='fam123', family_password='pass'
        )
        self.user = User.objects.create_user(
            username='user1', email='user1@example.com', password='pass', family=self.family
        )

        # カテゴリを作成
        self.category = MstShoppingItemCategory.objects.create(name='食品', order_id=1)
        self.other_category = MstShoppingItemCategory.objects.create(name='日用品', order_id=2)

        # テンプレートを作成
        self.template = ShoppingItemTemplate.objects.create(
            shopping_item_category=self.category,
            item_name='牛乳',
            memo='1本',
            family=self.family,
            order_id=1
        )

        # 通知タイプ・メソッドを作成 (order_id は必須項目)
        self.nt = MstNotifyType.objects.create(
            name='add_shopping_list',
            order_id=1
        )
        self.nm = MstNotifyMethod.objects.create(
            name='line_official',
            order_id=1
        )

    def test_get_not_logged_in(self):
        # 家族・ユーザーを作成
        self.family = Family.objects.create(
            family_authentication_id='fam123', family_password='pass'
        )
        self.user = User.objects.create_user(
            username='user1', email='user1@example.com', password='pass', family=self.family
        )

        # カテゴリを作成
        self.category = MstShoppingItemCategory.objects.create(name='食品', order_id=1)
        self.other_category = MstShoppingItemCategory.objects.create(name='日用品', order_id=2)

        # テンプレートを作成
        self.template = ShoppingItemTemplate.objects.create(
            shopping_item_category=self.category,
            item_name='牛乳',
            memo='1本',
            family=self.family,
            order_id=1
        )

        # 通知タイプ・メソッドを作成
        self.nt = MstNotifyType.objects.create(name='add_shopping_list')
        self.nm = MstNotifyMethod.objects.create(name='line_official')

    def test_get_not_logged_in(self):
        """未ログイン時はログイン画面にリダイレクトされる"""
        url = reverse('shopping_top')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_get_no_family(self):
        """ログイン済みだが family 未設定時は family_select にリダイレクト"""
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass')
        self.client.force_login(user2)
        url = reverse('shopping_top')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('family_select'))

    def test_get_success_and_context(self):
        """未完了アイテムとテンプレート、blank_form, add_forms が返る"""
        # 未完了アイテムを作成
        item = ShoppingItem.objects.create(
            shopping_item_category=self.category,
            item_name='卵',
            memo='6個',
            family=self.family,
            user=self.user,
            completion_flag=False
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('shopping_top'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shopping/top.html')
        self.assertIn(item, response.context['items'])
        # テンプレート一覧の検証
        templates = list(response.context['templates'])
        self.assertIn(
            {'id': self.template.id, 'shopping_item_category_id': self.category.id, 'item_name': self.template.item_name, 'memo': self.template.memo},
            templates
        )
        self.assertIsInstance(response.context['blank_form'], ShoppingItemRowForm)
        self.assertEqual(response.context['add_forms'], [])

    def test_post_add_item_without_template(self):
        """テンプレート未選択で正常追加"""
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        data = {
            'add_item': '1',
            'template_choice': '',
            'shopping_item_category': str(self.category.id),
            'item_name': 'パン',
            'memo': ''
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        self.assertTrue(ShoppingItem.objects.filter(item_name='パン', family=self.family, completion_flag=False).exists())

    def test_post_add_item_with_template(self):
        """テンプレート選択時にテンプレート内容で追加"""
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        data = {
            'add_item': '1',
            'template_choice': str(self.template.id),
            'shopping_item_category': str(self.other_category.id),
            'item_name': 'dummy',
            'memo': 'dummy'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        si = ShoppingItem.objects.filter(item_name=self.template.item_name, family=self.family).first()
        self.assertEqual(si.shopping_item_category, self.category)
        self.assertEqual(si.memo, self.template.memo)

    def test_post_add_item_invalid(self):
        """必須項目欠損でバリデーションエラー"""
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        data = {
            'add_item': '1',
            'template_choice': '',
            'shopping_item_category': '',
            'item_name': '',
            'memo': ''
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['add_forms'][0]
        self.assertIn('shopping_item_category', form.errors)
        self.assertEqual(form.errors['shopping_item_category'][0], 'このフィールドは必須です。')
        self.assertIn('item_name', form.errors)
        self.assertEqual(form.errors['item_name'][0], 'このフィールドは必須です。')

    def test_post_notify_manual_with_pending(self):
        """未完了アイテムがある場合に NotifySchedule 作成"""
        ShoppingItem.objects.create(
            shopping_item_category=self.category,
            item_name='卵',
            memo='',
            family=self.family,
            user=self.user,
            completion_flag=False
        )
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        response = self.client.post(url, {'notify_manual': '1'})
        self.assertRedirects(response, url)
        ns = NotifySchedule.objects.filter(family=self.family, notify_type=self.nt, notify_method=self.nm)
        self.assertEqual(ns.count(), 1)
        self.assertIn('・卵', ns.first().notify_content)

    def test_post_notify_manual_without_pending(self):
        """未完了アイテムなしでは NotifySchedule 作成しない"""
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        NotifySchedule.objects.all().delete()
        response = self.client.post(url, {'notify_manual': '1'})
        self.assertRedirects(response, url)
        self.assertFalse(NotifySchedule.objects.exists())

    def test_post_complete_id(self):
        """complete_id による完了フラグ更新"""
        item = ShoppingItem.objects.create(
            shopping_item_category=self.category,
            item_name='パン',
            memo='',
            family=self.family,
            user=self.user,
            completion_flag=False
        )
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        response = self.client.post(url, {'complete_id': str(item.id)})
        self.assertRedirects(response, url)
        item.refresh_from_db()
        self.assertTrue(item.completion_flag)

    def test_post_complete_invalid_id(self):
        """存在しない ID では何もしない"""
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        response = self.client.post(url, {'complete_id': '9999'})
        self.assertRedirects(response, url)

    def test_post_delete_id(self):
        """delete_id による論理削除"""
        item = ShoppingItem.objects.create(
            shopping_item_category=self.category,
            item_name='パン',
            memo='',
            family=self.family,
            user=self.user,
            completion_flag=False
        )
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        response = self.client.post(url, {'delete_id': str(item.id)})
        self.assertRedirects(response, url)
        item.refresh_from_db()
        self.assertIsNotNone(item.deleted_at)

    def test_post_delete_invalid_id(self):
        """存在しない ID でも例外にならずリダイレクト"""
        self.client.force_login(self.user)
        url = reverse('shopping_top')
        response = self.client.post(url, {'delete_id': '9999'})
        self.assertRedirects(response, url)
