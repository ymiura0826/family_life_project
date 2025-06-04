# ikujikanri/views/excretion_list.py
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from ikujikanri.models.excretion_record import ExcretionRecord
from account.models.child import Child

class ExcretionRecordListView(LoginRequiredMixin, ListView):
    template_name = 'ikujikanri/excretion_list.html'
    context_object_name = 'records'

    def get_queryset(self):
        child_id = self.kwargs['child_id']
        self.child = get_object_or_404(Child, pk=child_id, family=self.request.user.family)
        one_week_ago = timezone.now().date() - timedelta(days=7)
        return ExcretionRecord.objects.select_related('excretion_type').filter(
            child=self.child,
            deleted_at__isnull=True,
            action_at__date__gte=one_week_ago
        ).order_by('-action_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child'] = self.child
        return context
