# account/views/dashboard.py

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'common/dashboard.html' 

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.family:
            return redirect(reverse("family_select"))
        return super().dispatch(request, *args, **kwargs)
