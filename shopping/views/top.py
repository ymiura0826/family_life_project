from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

from shopping.forms import ShoppingItemRowForm
from shopping.models.shopping_item import ShoppingItem
from shopping.models.shopping_item_template import ShoppingItemTemplate
from notification.models.notify_schedule import NotifySchedule
from notification.models.notify_type import MstNotifyType
from notification.models.notify_method import MstNotifyMethod

class ShoppingTopView(LoginRequiredMixin, View):
    template_name = 'shopping/top.html'
    success_url   = reverse_lazy('shopping_top')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.family:
            return redirect(reverse_lazy('family_select'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        family = request.user.family
        items = ShoppingItem.objects.filter(
            family=family, deleted_at__isnull=True, completion_flag=False
        ).order_by('shopping_item_category_id', 'created_at')

        # JS 用にテンプレート一覧も渡す
        templates = ShoppingItemTemplate.objects.filter(
            family=family, deleted_at__isnull=True
        ).values('id', 'shopping_item_category_id', 'item_name', 'memo')

        # blank_form は JS で複製に使う
        blank_form = ShoppingItemRowForm(family=family)

        return render(request, self.template_name, {
            'items': items,
            'templates': templates,
            'add_forms': [],       # エラー時のみフォームを返す
            'blank_form': blank_form,
        })

    def post(self, request, *args, **kwargs):
        family = request.user.family

        # 1) 個別追加
        if 'add_item' in request.POST:
            form = ShoppingItemRowForm(request.POST, family=family)
            if form.is_valid():
                data = form.cleaned_data
                tpl_id = data.get('template_choice')
                if tpl_id:
                    tpl = ShoppingItemTemplate.objects.filter(
                        pk=int(tpl_id), family=family, deleted_at__isnull=True
                    ).first()
                    category, name, memo = tpl.shopping_item_category, tpl.item_name, tpl.memo or ''
                else:
                    category, name, memo = data['shopping_item_category'], data['item_name'], data['memo'] or ''

                ShoppingItem.objects.create(
                    shopping_item_category=category,
                    item_name=name,
                    memo=memo,
                    family=family,
                    user=request.user,
                    completion_flag=False,
                )
                return redirect(self.success_url)

            # バリデーションエラー時は再描画
            items = ShoppingItem.objects.filter(
                family=family, deleted_at__isnull=True, completion_flag=False
            ).order_by('shopping_item_category_id', 'created_at')
            templates = ShoppingItemTemplate.objects.filter(
                family=family, deleted_at__isnull=True
            ).values('id', 'shopping_item_category_id', 'item_name', 'memo')
            blank_form = ShoppingItemRowForm(family=family)
            return render(request, self.template_name, {
                'items': items,
                'templates': templates,
                'add_forms': [form],
                'blank_form': blank_form,
            })

        # 2) 手動通知
        if 'notify_manual' in request.POST:
            pending = ShoppingItem.objects.filter(
                family=family, deleted_at__isnull=True, completion_flag=False
            )
            if pending.exists():
                nt = MstNotifyType.objects.get(name='add_shopping_list')
                nm = MstNotifyMethod.objects.get(name='line_official')
                lines = [f"・{it.item_name}（{it.shopping_item_category.name}）" for it in pending]
                NotifySchedule.objects.create(
                    family=family,
                    notify_type=nt,
                    notify_method=nm,
                    schedule_at=timezone.now(),
                    notify_content="⚠ 未完了の買い物リストです。\n" + "\n".join(lines),
                )
            return redirect(self.success_url)

        # 3) 完了
        if 'complete_id' in request.POST:
            cid = int(request.POST['complete_id'])
            ShoppingItem.objects.filter(
                pk=cid, family=family, deleted_at__isnull=True, completion_flag=False
            ).update(completion_flag=True, updated_at=timezone.now())
            return redirect(self.success_url)

        # 4) 削除
        if 'delete_id' in request.POST:
            did = int(request.POST['delete_id'])
            try:
                item = ShoppingItem.objects.get(pk=did, family=family, deleted_at__isnull=True)
                item.deleted_at = timezone.now()
                item.save(update_fields=['deleted_at'])
            except ShoppingItem.DoesNotExist:
                pass
            return redirect(self.success_url)

        return redirect(self.success_url)
