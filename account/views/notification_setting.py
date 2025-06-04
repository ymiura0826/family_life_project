from django.views.generic.edit import UpdateView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from account.models.notification_setting import NotificationSetting
from account.forms import NotificationSettingForm
from django.contrib.auth.mixins import LoginRequiredMixin

class NotificationSettingDetailView(LoginRequiredMixin, UpdateView):
    model = NotificationSetting
    form_class = NotificationSettingForm
    template_name = 'account/notification_setting.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.family:
            return redirect(reverse("family_select"))
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        family = self.request.user.family
        setting, created = NotificationSetting.objects.get_or_create(
            family=family,
            defaults={
                'enable_notify_flag': True,
                'notify_method': None  # LINE Notify 固定のためここは使用しない
            }
        )
        return setting

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return "/setting/complete/"
