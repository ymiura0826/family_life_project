from django.test import TestCase
from django.contrib.auth.hashers import make_password
from account.forms import FamilyAuthForm
from account.models.family import Family


class FamilyAuthFormTest(TestCase):
    def setUp(self):
        self.family = Family.objects.create(
            family_authentication_id='test_family',
            family_password=make_password('correct_password'),
            line_notify_id='line123'
        )

    def test_valid_credentials(self):
        """TC01: 正しいIDとパスワードで認証成功"""
        form = FamilyAuthForm(data={
            'family_authentication_id': 'test_family',
            'family_password': 'correct_password'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['family_obj'], self.family)

    def test_missing_family_authentication_id(self):
        """TC02: family_authentication_id が空"""
        form = FamilyAuthForm(data={
            'family_authentication_id': '',
            'family_password': 'somepass'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('このフィールドは必須です。', form.errors['family_authentication_id'])

    def test_missing_family_password(self):
        """TC03: family_password が空"""
        form = FamilyAuthForm(data={
            'family_authentication_id': 'test_family',
            'family_password': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('このフィールドは必須です。', form.errors['family_password'])

    def test_invalid_family_id(self):
        """TC04: 存在しない family_authentication_id"""
        form = FamilyAuthForm(data={
            'family_authentication_id': 'not_exist',
            'family_password': 'any_password'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('その家族IDは登録されていません', form.non_field_errors())

    def test_wrong_password(self):
        """TC05: パスワードが一致しない"""
        form = FamilyAuthForm(data={
            'family_authentication_id': 'test_family',
            'family_password': 'wrong_password'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('パスワードが一致していません', form.non_field_errors())

    def test_valid_with_hashed_password(self):
        """TC06: 既にハッシュ化されたパスワードでも認証成功"""
        form = FamilyAuthForm(data={
            'family_authentication_id': 'test_family',
            'family_password': 'correct_password'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['family_obj'], self.family)
