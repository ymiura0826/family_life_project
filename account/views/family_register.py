# account/views/family_register.py
from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from account.forms import FamilyForm
from account.models.family import Family

class FamilyRegisterView(LoginRequiredMixin, FormView):
    template_name = 'account/family_register.html'
    form_class = FamilyForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.family:
            return redirect('/dashboard/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        family = form.save()
        self.request.user.family = family
        self.request.user.save()
        return super().form_valid(form)
