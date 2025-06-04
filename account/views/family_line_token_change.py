# account/views/family_line_token_change.py

from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from account.forms import FamilyLineTokenChangeForm

class FamilyLineTokenChangeView(LoginRequiredMixin, FormView):
    template_name = 'account/family_line_token_change.html'
    form_class = FamilyLineTokenChangeForm
    success_url = reverse_lazy('setting_complete')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['family'] = self.request.user.family
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()  # ログイン画面へ
        if not request.user.family:
            return redirect(reverse("family_select"))
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form):
        self.request.user.family.line_notify_id = form.cleaned_data['new_token']
        self.request.user.family.save()
        return super().form_valid(form)
