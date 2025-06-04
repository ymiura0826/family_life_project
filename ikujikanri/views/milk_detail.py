from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse
from django.http import Http404  # ← 追加
from ikujikanri.forms import MilkRecordForm
from ikujikanri.models.milk_record import MilkRecord

class MilkDetailView(UpdateView):
    model = MilkRecord
    form_class = MilkRecordForm
    template_name = 'ikujikanri/milk_detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        return MilkRecord.objects.filter(
            deleted_at__isnull=True,
            child__family=self.request.user.family
        )

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        form.save()
        return redirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        if "delete" in request.POST:
            pk = self.kwargs['pk']
            record = MilkRecord.objects.filter(
                pk=pk,
                child__family=self.request.user.family,
                deleted_at__isnull=True  # ← 追加
            ).first()
            if record:
                record.deleted_at = timezone.now()
                record.save()
                return redirect(reverse('milk_list', kwargs={'child_id': record.child.child_id}))
            raise Http404("Record not found or already deleted.")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        child_id = self.get_object().child.child_id
        return reverse('milk_list', kwargs={'child_id': child_id})
