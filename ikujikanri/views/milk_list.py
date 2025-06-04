from django.utils import timezone
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from datetime import timedelta
from ikujikanri.models.milk_record import MilkRecord
from account.models.child import Child

class MilkListView(ListView):
    model = MilkRecord
    template_name = 'ikujikanri/milk_list.html'
    context_object_name = 'records'

    def dispatch(self, request, *args, **kwargs):
        self.child = get_object_or_404(Child, pk=kwargs['child_id'], family=request.user.family)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        today = timezone.localdate()
        week_ago = today - timedelta(days=7)
        return (
            MilkRecord.objects
            .filter(child=self.child, action_at__date__gte=week_ago, deleted_at__isnull=True)
            .order_by('-action_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child'] = self.child
        return context
