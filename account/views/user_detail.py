# account/views/user_detail.py

from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/user_detail.html'
    context_object_name = 'user_obj'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.family:
            return redirect('family_select')
        if request.user.id != int(kwargs['pk']):
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


