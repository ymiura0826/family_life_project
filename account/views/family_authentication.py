# account/views/family_authentication.py

from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from account.forms import FamilyAuthForm

class FamilyAuthenticationView(LoginRequiredMixin, FormView):
    template_name = 'account/family_authentication.html'
    form_class = FamilyAuthForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.family:
            return redirect('/dashboard/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        family = form.cleaned_data['family_obj']
        self.request.user.family = family
        self.request.user.save()
        return super().form_valid(form)
