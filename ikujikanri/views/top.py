from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from account.models.child import Child
from ikujikanri.models.milk_record import MilkRecord
from ikujikanri.models.excretion_record import ExcretionRecord
from django.utils.timezone import localdate
from datetime import timedelta

class IkujiTopView(LoginRequiredMixin, TemplateView):
    template_name = 'ikujikanri/top.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = localdate()
        yesterday = today - timedelta(days=1)
        children = Child.objects.filter(family=self.request.user.family, deleted_at__isnull=True).order_by('birth_date')

        records = []
        for child in children:
            last_milk = (
                MilkRecord.objects
                .filter(child=child, deleted_at__isnull=True)
                .order_by('-action_at')
                .first()
            )

            ex_today = ExcretionRecord.objects.filter(child=child, action_at__date=today, deleted_at__isnull=True)
            ex_yesterday = ExcretionRecord.objects.filter(child=child, action_at__date=yesterday, deleted_at__isnull=True)

            today_stats = {
                'pee': ex_today.filter(excretion_type__name='おしっこ').count(),
                'poo': ex_today.filter(excretion_type__name='うんち').count(),
            }
            yesterday_stats = {
                'pee': ex_yesterday.filter(excretion_type__name='おしっこ').count(),
                'poo': ex_yesterday.filter(excretion_type__name='うんち').count(),
            }

            records.append({
                'child': child,
                'last_milk': last_milk,
                'today_stats': today_stats,
                'yesterday_stats': yesterday_stats,
            })

        context['records'] = records
        return context
