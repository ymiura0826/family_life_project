# account/views/family_detail.py

from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from account.models.family import Family

class FamilyDetailView(LoginRequiredMixin, DetailView):
    model = Family
    template_name = 'account/family_detail.html'
    context_object_name = 'family'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.family:
            return redirect(reverse("family_select"))
        if request.user.family.family_id != int(kwargs['pk']):
            return redirect('/dashboard/')
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family = self.request.user.family
        context['family'] = family
        context['active_children'] = family.children.filter(deleted_at__isnull=True)
        return context