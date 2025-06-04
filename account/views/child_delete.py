# account/views/child_delete.py

from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from account.models.child import Child

class ChildDeleteView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.family:
            return redirect(reverse("family_select"))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        child = get_object_or_404(Child, pk=pk, family=request.user.family)
        child.deleted_at = timezone.now()
        child.save()
        return redirect('setting_complete')
