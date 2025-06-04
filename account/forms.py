# account/forms.py

from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from .models.family import Family
from .models.child import Child
from .models.notification_setting import NotificationSetting
from .models.sex import MstSex

User = get_user_model()#カスタムユーザーモデルの情報取得

class CustomUserForm(UserCreationForm):
    error_messages = {
        "password_mismatch": "確認用パスワードが一致しません",
    }

    class Meta:
        model = User
        fields = ['username', 'email']
        error_messages = {
            'username': {
                'required': 'このフィールドは必須です。',
            },
            'email': {
                'required': 'このフィールドは必須です。',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['username'].label = 'ユーザー名'
        self.fields['email'].label = 'メールアドレス'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認用）'
    
    # password1, password2 のエラーメッセージを個別に上書き
        self.fields['password1'].error_messages['required'] = 'このフィールドは必須です。'
        self.fields['password2'].error_messages['required'] = 'このフィールドは必須です。'


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('メールアドレスは登録済みです')
        return email

class UserPasswordChangeForm(forms.Form):
    current_password = forms.CharField(label='現在のパスワード', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})
    new_password = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})
    confirm_password = forms.CharField(label='新しいパスワード（確認）', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        

    def clean(self):
        cleaned_data = super().clean()
        current_pw = cleaned_data.get("current_password")
        new_pw = cleaned_data.get("new_password")
        confirm_pw = cleaned_data.get("confirm_password")

        if not check_password(current_pw, self.user.password):
            raise forms.ValidationError("パスワードが違います")

        if new_pw != confirm_pw:
            raise forms.ValidationError("新しいパスワードが一致しません")

        return cleaned_data

    def save(self, commit=True):
        self.user.password = make_password(self.cleaned_data["new_password"])
        if commit:
            self.user.save()
        return self.user

class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ['family_authentication_id', 'family_password', 'line_notify_id']
        widgets = {
            'family_password': forms.PasswordInput(),
        }
        error_messages = {
            'family_authentication_id': {
                'required': 'このフィールドは必須です。',
            },
            'family_password': {
                'required': 'このフィールドは必須です。',
            },
            'line_notify_id': {
                'required': 'このフィールドは必須です。',
            },
        }

    def clean_family_password(self):
        pw = self.cleaned_data['family_password']
        if pw and not pw.startswith('pbkdf2_'):
            return make_password(pw)
        return pw

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['family_authentication_id'].label = '家族ID'
        self.fields['family_password'].label = '家族パスワード'
        self.fields['line_notify_id'].label = 'LINE Group Id'

    def clean_family_authentication_id(self):
        family_id = self.cleaned_data['family_authentication_id']
        if Family.objects.filter(family_authentication_id=family_id).exists():
            raise forms.ValidationError('この家族IDは登録済みです')
        return family_id

class FamilyAuthForm(forms.Form):
    family_authentication_id = forms.CharField(
        label="家族ID",
        error_messages={'required': 'このフィールドは必須です。'}
    )
    family_password = forms.CharField(
        label="家族パスワード",
        widget=forms.PasswordInput,
        error_messages={'required': 'このフィールドは必須です。'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.pop('required', None)  # HTMLの吹き出し抑止

    def clean(self):
        cleaned_data = super().clean()
        family_id = cleaned_data.get("family_authentication_id")
        password = cleaned_data.get("family_password")

        from account.models.family import Family
        from django.contrib.auth.hashers import check_password

        try:
            family = Family.objects.get(family_authentication_id=family_id)
        except Family.DoesNotExist:
            raise forms.ValidationError("その家族IDは登録されていません")

        if not check_password(password, family.family_password):
            raise forms.ValidationError("パスワードが一致していません")

        cleaned_data["family_obj"] = family
        return cleaned_data

class FamilyPasswordChangeForm(forms.Form):
    current_password = forms.CharField(label='現在のパスワード', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})
    new_password = forms.CharField(label='新しいパスワード', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})
    confirm_password = forms.CharField(label='新しいパスワード（確認）', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})

    def __init__(self, *args, **kwargs):
        self.family = kwargs.pop('family', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        current_pw = cleaned_data.get("current_password")
        new_pw = cleaned_data.get("new_password")
        confirm_pw = cleaned_data.get("confirm_password")

        if not check_password(current_pw, self.family.family_password):
            raise forms.ValidationError("パスワードが違います")

        if new_pw != confirm_pw:
            raise forms.ValidationError("新しいパスワードが一致しません")

        return cleaned_data

class FamilyLineTokenChangeForm(forms.Form):
    current_password = forms.CharField(label='現在のパスワード', widget=forms.PasswordInput,error_messages={'required': 'このフィールドは必須です。'})
    new_token = forms.CharField(label='新しいLINE Group Id', widget=forms.TextInput,error_messages={'required': 'このフィールドは必須です。'})

    def __init__(self, *args, **kwargs):
        self.family = kwargs.pop('family', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("current_password")
        if not check_password(pw, self.family.family_password):
            raise forms.ValidationError("パスワードが違います")
        return cleaned_data


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'birth_date', 'sex']
        labels = {
            'name': '名前',
            'birth_date': '誕生日',
            'sex': '性別',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'name': {'required': 'このフィールドは必須です。'},
            'birth_date': {'required': 'このフィールドは必須です。'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sex'].queryset = MstSex.objects.order_by('order_id')
        self.fields['sex'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.pop('required', None)


class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['enable_notify_flag']
        labels = {
            'enable_notify_flag': '育児管理通知を有効にする',
        }
        widgets = {
            'enable_notify_flag': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] += ' mb-3'

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'ユーザー名'
        self.fields['password'].label = 'パスワード'

        self.fields['username'].error_messages['required'] = 'このフィールドは必須です。'
        self.fields['password'].error_messages['required'] = 'このフィールドは必須です。'

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'