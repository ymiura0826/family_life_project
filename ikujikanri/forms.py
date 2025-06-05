from django import forms
from django.utils.timezone import now, localtime
from .models.milk_record import MilkRecord
from .models.excretion_record import ExcretionRecord
from ikujikanri.models.milk_type import MstMilkType
from ikujikanri.models.excretion_type import MstExcretionType
from ikujikanri.models.excretion_record import ExcretionRecord

class MilkRecordForm(forms.ModelForm):
    notify_flag = forms.BooleanField(required=False, label="次回ミルク通知を設定する")
    next_milk_at = forms.DateTimeField(
        required=False,
        label='次回ミルク予定日時',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        #initial=localtime(now()).replace(second=0, microsecond=0),
    )

    class Meta:
        model = MilkRecord
        fields = [
            'action_at', 'milk_type', 'amount',
            'left_breast_minutes', 'right_breast_minutes'
        ]
        labels = {
            'action_at': '実施日時',
            'milk_type': 'ミルクの種類',
            'amount': 'ミルクの量',
            'left_breast_minutes': '左の授乳時間',
            'right_breast_minutes': '右の授乳時間',
        }
        widgets = {
            'action_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'amount': forms.Select(choices=[(i, f'{i} ml') for i in range(5, 205, 5)]),
            'left_breast_minutes': forms.Select(choices=[(i, f'{i} 分') for i in range(1, 21)]),
            'right_breast_minutes': forms.Select(choices=[(i, f'{i} 分') for i in range(1, 21)]),
        }
        error_messages = {
            'milk_type': {
                'required': 'このフィールドは必須です。'
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['milk_type'].queryset = MstMilkType.objects.order_by('order_id')
        self.fields['milk_type'].required = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.pop('required', None)

        self.fields['notify_flag'].widget.attrs['class'] = 'form-check-input'
        self.fields['next_milk_at'].widget.attrs['class'] = 'form-control'
        self.fields['next_milk_at'].initial = localtime(now()).replace(second=0, microsecond=0)

    def clean(self):
        cleaned_data = super().clean()
        milk_type = cleaned_data.get('milk_type')
        amount = cleaned_data.get('amount')
        left = cleaned_data.get('left_breast_minutes')
        right = cleaned_data.get('right_breast_minutes')
        notify_flag = cleaned_data.get('notify_flag')
        next_milk_at = cleaned_data.get('next_milk_at')

        if milk_type:
            if milk_type.name == '母乳':
                if left is None and right is None:
                    raise forms.ValidationError('母乳の場合は左右いずれかの授乳時間を入力してください。')
            else:
                if amount is None:
                    raise forms.ValidationError('粉ミルクまたは搾乳の場合は量を入力してください。')

        if notify_flag and not next_milk_at:
            raise forms.ValidationError('通知設定が有効な場合は次回ミルク予定日時を入力してください。')

        return cleaned_data

class ExcretionRecordForm(forms.Form):
    action_at = forms.DateTimeField(
        label='実施日時',
        #initial=localtime(now()).replace(second=0, microsecond=0),
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        error_messages={
            'required': 'このフィールドは必須です。',
            'invalid': '正しい日時を入力してください。',
        }
    )

    excretion_type = forms.ChoiceField(
        label='排泄の種類',
        choices=[
            ('', '---------'),
            ('1', 'おしっこ'),
            ('2', 'うんち'),
            ('99', 'おしっこ・うんち'),
        ],
        error_messages={
            'required': '排泄の種類を選択してください。',
        }
    )

    memo = forms.CharField(
        label='メモ',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['action_at'].initial = localtime(now()).replace(second=0, microsecond=0)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs.pop('required', None)
            else:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs.pop('required', None)

    def clean_excretion_type(self):
        value = self.cleaned_data.get('excretion_type')
        if value == '':
            raise forms.ValidationError('排泄の種類を選択してください。')
        return value


class ExcretionRecordUpdateForm(forms.ModelForm):
    class Meta:
        model = ExcretionRecord
        fields = ['action_at', 'excretion_type', 'memo']
        labels = {
            'action_at': '実施日時',
            'excretion_type': '排泄の種類',
            'memo': 'メモ',
        }
        widgets = {
            'action_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'memo': forms.Textarea(attrs={'rows': 2}),
        }
        error_messages = {
            'action_at': {'required': 'このフィールドは必須です。'},
            'excretion_type': {'required': 'このフィールドは必須です。'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['excretion_type'].queryset = MstExcretionType.objects.order_by('order_id')
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.pop('required', None)

    def clean_excretion_type(self):
        value = self.cleaned_data.get('excretion_type')
        if value is None:
            raise forms.ValidationError('排泄の種類を選択してください。')
        return value

    def clean_action_at(self):
        value = self.cleaned_data.get('action_at')
        if not value:
            raise forms.ValidationError('実施日時を入力してください。')
        return value