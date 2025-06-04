from django.test import TestCase
from account.forms import FamilyForm
from account.models.family import Family

class FamilyFormTest(TestCase):
    def setUp(self):
        # 重複チェック用データ
        self.existing_family = Family.objects.create(
            family_authentication_id='existing_id',
            family_password='pbkdf2_sha256$alreadyhashed',
            line_notify_id='notify_token_123'
        )

    def test_valid_form_creates_family(self):
        """TC01: 正常な入力でフォームが有効かつ保存可能"""
        form = FamilyForm(data={
            'family_authentication_id': 'new_family',
            'family_password': 'securepass123',
            'line_notify_id': 'line_abc123'
        })
        self.assertTrue(form.is_valid())
        family = form.save()
        self.assertTrue(family.family_password.startswith('pbkdf2_'))

    def test_missing_family_authentication_id(self):
        """TC02: family_authentication_id 未入力でエラー"""
        form = FamilyForm(data={
            'family_authentication_id': '',
            'family_password': 'somepass',
            'line_notify_id': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('family_authentication_id', form.errors)
        self.assertIn('このフィールドは必須です。', form.errors['family_authentication_id'])

    def test_missing_family_password(self):
        """TC03: family_password 未入力でエラー"""
        form = FamilyForm(data={
            'family_authentication_id': 'some_id',
            'family_password': '',
            'line_notify_id': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('family_password', form.errors)
        self.assertIn('このフィールドは必須です。', form.errors['family_password'])

    def test_blank_line_notify_id(self):
        """TC04: line_notify_id 未入力でもエラーにならない"""
        form = FamilyForm(data={
            'family_authentication_id': 'another_family',
            'family_password': 'pass123',
            'line_notify_id': ''
        })
        self.assertTrue(form.is_valid())

    def test_duplicate_family_authentication_id(self):
        """TC05: family_authentication_id 重複時にエラー"""
        form = FamilyForm(data={
            'family_authentication_id': 'existing_id',
            'family_password': 'newpass123',
            'line_notify_id': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('この家族IDは登録済みです', form.errors['family_authentication_id'])

    def test_password_is_hashed(self):
        """TC06: 保存時にpasswordがハッシュ化される"""
        form = FamilyForm(data={
            'family_authentication_id': 'hash_test',
            'family_password': 'plainpassword',
            'line_notify_id': ''
        })
        self.assertTrue(form.is_valid())
        family = form.save()
        self.assertTrue(family.family_password.startswith('pbkdf2_'))

    def test_already_hashed_password_not_rehashed(self):
        """TC07: すでにハッシュ化されたパスワードは再ハッシュされない"""
        form = FamilyForm(data={
            'family_authentication_id': 'rehash_test',
            'family_password': 'pbkdf2_sha256$alreadyhashed',
            'line_notify_id': ''
        })
        self.assertTrue(form.is_valid())
        family = form.save()
        self.assertEqual(family.family_password, 'pbkdf2_sha256$alreadyhashed')

    def test_line_notify_id_saved(self):
        """TC08: 任意のline_notify_idが保存される"""
        form = FamilyForm(data={
            'family_authentication_id': 'notify_test',
            'family_password': 'somepassword',
            'line_notify_id': 'line_test_id_999'
        })
        self.assertTrue(form.is_valid())
        family = form.save()
        self.assertEqual(family.line_notify_id, 'line_test_id_999')
