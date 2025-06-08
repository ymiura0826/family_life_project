# shopping/forms.py

from django import forms
from django.forms import formset_factory
from shopping.models.shopping_item import ShoppingItem
from shopping.models.shopping_item_template import ShoppingItemTemplate
from shopping.models.shopping_item_category import MstShoppingItemCategory
from django.utils import timezone

class ShoppingItemRowForm(forms.ModelForm):
    """
    買い物リストの 1 行分を扱うフォーム。
    ・テンプレート選択用の ChoiceField（template_choice）を追加し、
      JavaScript で選択されたテンプレートに従って
      'shopping_item_category' と 'item_name' を自動反映する想定。
    """
    # 「よく使うものテンプレート」を選べるドロップダウン
    template_choice = forms.ChoiceField(
        label='テンプレート選択',
        required=False,
        # 初期 choices は空。一度 __init__ で書き換える。
        choices=[('', '── よく買うものから選ぶ ──')],
        widget=forms.Select(attrs={'class': 'form-select template-select'})
    )

    class Meta:
        model = ShoppingItem
        # completion_flag は追加直後は常に False なので、ここには含めない。
        fields = [
            'shopping_item_category',
            'item_name',
            'memo',
        ]
        widgets = {
            'shopping_item_category': forms.Select(attrs={'class': 'form-select'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'アイテム名'}),
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'メモ（任意）'}),
        }
        labels = {
            'shopping_item_category': 'カテゴリ',
            'item_name': 'アイテム名',
            'memo': 'メモ',
        }
        error_messages = {
            'shopping_item_category': {
                'required': 'このフィールドは必須です。'
            },
            'item_name': {
                'required': 'このフィールドは必須です。'
            },
            # memo は任意なので不要
        }

    def __init__(self, *args, **kwargs):
        # 初期値として family を受け取っておく想定
        family = kwargs.pop('family', None)
        super().__init__(*args, **kwargs)

        # ① 「よく使うもの」テンプレートをこの家族に絞って choices に設定
        if family:
            templates = ShoppingItemTemplate.objects.filter(family=family,deleted_at__isnull=True).order_by('order_id')
        else:
            templates = ShoppingItemTemplate.objects.none()

        # ChoiceField 用の choices を改めて準備
        choices = [('', '── よく買うものから選ぶ ──')]
        for t in templates:
            # 表示ラベルに「アイテム名（カテゴリ名）」を含めておく
            label = f"{t.item_name}（{t.shopping_item_category.name}）"
            choices.append((str(t.id), label))

        self.fields['template_choice'].choices = choices

        # ② 「テンプレートから選択」以外に、カテゴリとアイテム名を自分で入力できるようにする
        #     ※ 初回表示時はカテゴリ・アイテム名とも空なので、フォームに「空の選択肢」も追加
        self.fields['shopping_item_category'].empty_label = '――選択してください――'
        self.fields['item_name'].required = True
        self.fields['memo'].required = False


# 「一度に 3 行分ぐらい表示 → 必要に応じて追加できる」フォームセットを定義
ShoppingItemFormSet = formset_factory(
    ShoppingItemRowForm,
    extra=3,       # まずは 3 行分を表示
    max_num=10,    # 最大 10 行まで
    validate_max=True,
    can_delete=True  # 行の削除チェックボックスを表示
)

class ShoppingItemEditForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        # 編集画面で表示・更新するフィールドを指定
        fields = [
            'shopping_item_category',
            'item_name',
            'memo',
        ]
        widgets = {
            'shopping_item_category': forms.Select(attrs={'class': 'form-select'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'アイテム名'}),
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'メモ（任意）'}),
        }
        labels = {
            'shopping_item_category': 'カテゴリ',
            'item_name': 'アイテム名',
            'memo': 'メモ',
        }
        error_messages = {
            'shopping_item_category': {
                'required': 'このフィールドは必須です。'
            },
            'item_name': {
                'required': 'このフィールドは必須です。'
            },
            # memo は任意なので不要
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['memo'].required = False

    def clean_shopping_item_category(self):
        category = self.cleaned_data.get('shopping_item_category')
        if category is None:
            raise forms.ValidationError('カテゴリは必須です。')
        return category

    def clean_item_name(self):
        name = self.cleaned_data.get('item_name')
        if not name or name.strip() == '':
            raise forms.ValidationError('アイテム名は必須です。')
        return name

class ShoppingItemTemplateForm(forms.ModelForm):
    """
    ShoppingItemTemplate を編集／新規追加するためのフォーム。
    ・order_id は HiddenInput でドラッグ＆ドロップ後に JS で書き換える。
    ・can_delete=True のフォームセットで、DELETE フラグを使って論理削除を行う。
    """

    class Meta:
        model = ShoppingItemTemplate
        # 家族フィールドは View で自動セットするのでフォームには含めない
        fields = [
            'shopping_item_category',
            'item_name',
            'memo',
            'order_id',
        ]
        widgets = {
            'shopping_item_category': forms.Select(attrs={'class': 'form-select'}),
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'アイテム名'}),
            'memo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'メモ（任意）'}),
            'order_id': forms.HiddenInput(),
        }
        labels = {
            'shopping_item_category': 'カテゴリ',
            'item_name': 'アイテム名',
            'memo': 'メモ',
        }
        error_messages = {
            'shopping_item_category': {
                'required': 'このフィールドは必須です。'
            },
            'item_name': {
                'required': 'このフィールドは必須です。'
            },
            # memo は任意なので不要
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['memo'].required = False

    def clean_shopping_item_category(self):
        category = self.cleaned_data.get('shopping_item_category')
        if category is None:
            raise forms.ValidationError('カテゴリは必須です。')
        return category

    def clean_item_name(self):
        name = self.cleaned_data.get('item_name')
        if not name or name.strip() == '':
            raise forms.ValidationError('アイテム名は必須です。')
        return name