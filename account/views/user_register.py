# account/views/user_register.py
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import get_user_model, login
from account.forms import CustomUserForm

User = get_user_model()

class UserRegisterView(FormView):
    template_name = 'account/user_register.html'
    form_class = CustomUserForm
    success_url = reverse_lazy('family_select')  # 家族登録ページへ

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/dashboard/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
