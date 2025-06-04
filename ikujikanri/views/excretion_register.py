from django.views.generic import FormView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from ikujikanri.forms import ExcretionRecordForm
from ikujikanri.models.excretion_record import ExcretionRecord
from ikujikanri.models.excretion_type import MstExcretionType
from account.models.child import Child

class ExcretionRecordRegisterView(FormView):
    template_name = 'ikujikanri/excretion_register.html'
    form_class = ExcretionRecordForm

    def dispatch(self, request, *args, **kwargs):
        self.child = get_object_or_404(Child, pk=kwargs['child_id'], family=request.user.family)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['child'] = self.child
        return context

    def form_valid(self, form):
        action_at = form.cleaned_data['action_at']
        memo = form.cleaned_data['memo']
        excretion_type = form.cleaned_data['excretion_type']

        if excretion_type == '99':
            for type_id in ['1', '2']:
                ex_type = get_object_or_404(MstExcretionType, pk=type_id, deleted_at__isnull=True)
                ExcretionRecord.objects.create(
                    child=self.child,
                    action_at=action_at,
                    memo=memo,
                    excretion_type=ex_type,
                )
        else:
            ex_type = get_object_or_404(MstExcretionType, pk=excretion_type, deleted_at__isnull=True)
            ExcretionRecord.objects.create(
                child=self.child,
                action_at=action_at,
                memo=memo,
                excretion_type=ex_type,
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('ikujikanri_top')
