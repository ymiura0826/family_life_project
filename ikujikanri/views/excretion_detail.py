from django.views.generic import UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from ikujikanri.models.excretion_record import ExcretionRecord
from ikujikanri.forms import ExcretionRecordUpdateForm

class ExcretionRecordDetailView(UpdateView):
    model = ExcretionRecord
    form_class = ExcretionRecordUpdateForm
    template_name = 'ikujikanri/excretion_detail.html'
    pk_url_kwarg = 'excretion_record_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['record'] = self.get_object()  # ← record.child.name に使う用
        return context

    def get_queryset(self):
        return ExcretionRecord.objects.filter(
            deleted_at__isnull=True,
            child__family=self.request.user.family
        )

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        # form_valid() の場合は self.object が設定されるので OK
        record = getattr(self, 'object', None)
        if record and record.child:
            return reverse('excretion_list', kwargs={'child_id': record.child.child_id})
        else:
            return reverse('ikujikanri_top')

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            obj = self.get_object()
            obj.deleted_at = timezone.now()
            obj.save()
            # 明示的に child_id を使って遷移
            if obj.child:
                return redirect('excretion_list', child_id=obj.child.child_id)
            else:
                return redirect('ikujikanri_top')
        return super().post(request, *args, **kwargs)
