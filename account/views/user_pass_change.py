from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from account.forms import UserPasswordChangeForm  # 自作フォームを使用
from django.contrib.auth import update_session_auth_hash

class UserPasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'account/user_pass_change.html'
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('setting_complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # フォームに user を渡す
        return kwargs

    def form_valid(self, form):
        form.save()  # パスワード保存（ハッシュ化付き）
        update_session_auth_hash(self.request, form.user)  # セッションを維持
        messages.success(self.request, 'パスワードを変更しました。')
        return super().form_valid(form)
