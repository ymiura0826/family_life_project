# account/views/family_select.py

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

class FamilySelectView(LoginRequiredMixin, TemplateView):
    template_name = 'account/family_select.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.family:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
