from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import modelformset_factory

from shopping.forms import ShoppingItemTemplateForm
from shopping.models.shopping_item_template import ShoppingItemTemplate


class ShoppingTemplateEditView(LoginRequiredMixin, View):
    """
    よく買うアイテムリスト編集（一括保存）
    ・既存テンプレートの編集、削除
    ・新規テンプレートの追加
    ・並び順の矢印で order_id を更新
    ・一括保存ボタンでまとめて DB 更新／論理削除
    """
    template_name = 'shopping/template_edit.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.family:
            return redirect(reverse_lazy('family_select'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, family_id):
        family = request.user.family
        if family.family_id != int(family_id):
            return redirect('shopping_template_edit', family_id=family.family_id)

        # FormSet 定義：extra=0 で初期フォームなし、can_delete=True で削除チェック
        TemplateFormSet = modelformset_factory(
            ShoppingItemTemplate,
            form=ShoppingItemTemplateForm,
            extra=0,
            can_delete=True
        )
        queryset = ShoppingItemTemplate.objects.filter(
            family=family, deleted_at__isnull=True
        ).order_by('order_id')
        formset = TemplateFormSet(queryset=queryset)
        return render(request, self.template_name, {
            'formset': formset,
            'family_id': family.family_id,
        })

    def post(self, request, family_id):
        family = request.user.family
        if family.family_id != int(family_id):
            return redirect('shopping_template_edit', family_id=family.family_id)

        TemplateFormSet = modelformset_factory(
            ShoppingItemTemplate,
            form=ShoppingItemTemplateForm,
            extra=0,
            can_delete=True
        )
        formset = TemplateFormSet(request.POST)

        # バリデーション: 削除予定のフォームはスキップ
        formset.is_valid()  # cleaned_data, errors を生成
        all_valid = True
        for form in formset.forms:
            # 削除がチェックされている場合はバリデーションをスキップ
            if form.cleaned_data.get('DELETE'):
                continue
            # 削除対象でないフォームにエラーがある場合は保存不可
            if form.errors:
                all_valid = False
                break

        if all_valid:
            # 論理削除：deleted_forms でチェックされたものを処理
            for form in getattr(formset, 'deleted_forms', []):
                obj = form.instance
                obj.deleted_at = timezone.now()
                obj.save(update_fields=['deleted_at'])

            # 追加・更新対象を保存
            instances = formset.save(commit=False)
            for inst in instances:
                inst.family = family
                inst.save()

            return redirect('shopping_template_edit', family_id=family.family_id)


        TemplateFormSet = modelformset_factory(
            ShoppingItemTemplate,
            form=ShoppingItemTemplateForm,
            extra=0,
            can_delete=True
        )
        formset = TemplateFormSet(request.POST)

        if formset.is_valid():
            # 論理削除：deleted_forms でチェックされたものを処理
            for form in formset.deleted_forms:
                obj = form.instance
                obj.deleted_at = timezone.now()
                obj.save(update_fields=['deleted_at'])

            # 追加・更新対象を保存
            instances = formset.save(commit=False)
            for inst in instances:
                inst.family = family
                inst.save()

            return redirect('shopping_template_edit', family_id=family.family_id)

        # バリデーションエラーの場合は再描画
        return render(request, self.template_name, {
            'formset': formset,
            'family_id': family.family_id,
        })
