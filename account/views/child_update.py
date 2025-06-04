from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from account.models.child import Child
from account.forms import ChildForm

class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    form_class = ChildForm
    template_name = 'account/child_update.html'
    success_url = reverse_lazy('setting_complete')

    def dispatch(self, request, *args, **kwargs):  
        if not request.user.is_authenticated:
            return self.handle_no_permission()  # LoginRequiredMixin に準拠（リダイレクト）
        if not request.user.family:
            return redirect("family_select")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Child.objects.filter(deleted_at__isnull=True, family=self.request.user.family)

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)
