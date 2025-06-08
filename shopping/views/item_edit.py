# shopping/views/item_edit.py

from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from shopping.models.shopping_item import ShoppingItem
from shopping.forms import ShoppingItemEditForm

class ShoppingItemUpdateView(LoginRequiredMixin, UpdateView):
    """
    個別の ShoppingItem を編集し、同画面に論理削除ボタンを配置する。
    編集 or 削除いずれの後も shopping_top にリダイレクト。
    """
    model = ShoppingItem
    form_class = ShoppingItemEditForm
    template_name = 'shopping/item_edit.html'
    # 削除・更新後のリダイレクト先
    success_url = reverse_lazy('shopping_top')

    def dispatch(self, request, *args, **kwargs):
        """
        ・LoginRequiredMixin によって未ログインはログイン画面へリダイレクトされる
        ・ここでは「family 未設定 → family_select 画面へリダイレクト」を追加
        """
        if not request.user.family:
            return redirect(reverse_lazy('family_select'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        編集対象は、自分の家族に紐づき、
        かつdeleted_at が null のレコードに限定する
        """
        return ShoppingItem.objects.filter(
            family=self.request.user.family,
            deleted_at__isnull=True
        )

    def form_valid(self, form):
        """
        「保存」ボタン押下時の処理：
        ・ModelForm による通常の更新
        """
        # form.instance.family や user は既に存在しているので設定不要
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        """
        POST時に「action」の値をチェックして処理を分岐：
        · action="delete" → 論理削除
        · それ以外（保存） → 普通に form_valid を呼ぶ
        """
        self.object = self.get_object()
        action = request.POST.get('action')

        if action == 'delete':
            # 論理削除
            self.object.deleted_at = timezone.now()
            self.object.save(update_fields=['deleted_at'])
            return redirect(self.success_url)

        # それ以外は「保存」
        return super().post(request, *args, **kwargs)
