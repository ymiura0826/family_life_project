# account/views/family_pass_change.py

from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from account.forms import FamilyPasswordChangeForm
from django.contrib.auth.hashers import make_password

class FamilyPassChangeView(LoginRequiredMixin, FormView):
    template_name = 'account/family_pass_change.html'
    form_class = FamilyPasswordChangeForm
    success_url = reverse_lazy('setting_complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['family'] = self.request.user.family
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()  # → LOGIN_URL にリダイレクト
        if not request.user.family:
            return redirect('/family_select/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        family = self.request.user.family
        new_password = form.cleaned_data['new_password']
        family.family_password = make_password(new_password)
        family.save()
        return super().form_valid(form)
