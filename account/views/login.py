# account/views/login.py

from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from account.forms import CustomLoginForm  # ← 追加

class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True
    form_class = CustomLoginForm  # ← 追加
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.family is None:
            return redirect('family_select')
        return redirect('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'IDもしくはパスが間違っています')
        return super().form_invalid(form)
