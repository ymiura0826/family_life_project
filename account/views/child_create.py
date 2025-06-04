from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models.child import Child
from account.forms import ChildForm


class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    form_class = ChildForm
    template_name = 'account/child_create.html'
    success_url = reverse_lazy('setting_complete')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.family:
            return redirect(reverse("family_select"))  # ← ✅ 追加：family未設定時の対応
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.family = self.request.user.family
        return super().form_valid(form)
