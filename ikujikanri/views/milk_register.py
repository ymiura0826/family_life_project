from django.views.generic import FormView
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now, localtime
from datetime import timedelta
from ikujikanri.forms import MilkRecordForm
from account.models.child import Child
from ikujikanri.models.milk_record import MilkRecord
from notification.models.notify_schedule import NotifySchedule
from notification.models.notify_type import MstNotifyType
from notification.models.notify_method import MstNotifyMethod

class MilkRegisterView(FormView):
    template_name = 'ikujikanri/milk_register.html'
    form_class = MilkRecordForm

    def dispatch(self, request, *args, **kwargs):
        self.child = get_object_or_404(Child, pk=kwargs['child_id'], family=request.user.family)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {
            'action_at': now().replace(second=0, microsecond=0),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child'] = self.child
        return context

    def form_valid(self, form):
        record = form.save(commit=False)
        record.child = self.child
        record.save()

        if form.cleaned_data.get('notify_flag') and form.cleaned_data.get('next_milk_at'):
            notify_time = form.cleaned_data['next_milk_at'] - timedelta(minutes=30)

            NotifySchedule.objects.create(
                family=self.request.user.family,
                notify_type=MstNotifyType.objects.get(name='milk'),
                notify_method=MstNotifyMethod.objects.get(name='line_official'),
                schedule_at=notify_time,
                notify_content=f"{self.child.name}の次回ミルクは{localtime(next_milk_at).strftime('%H:%M')}です"
            )

        return redirect('ikujikanri_top')  # ← URL name に合わせて修正
