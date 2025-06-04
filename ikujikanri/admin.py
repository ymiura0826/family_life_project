from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    MilkRecord,
    ExcretionRecord,
    MstMilkType,
    MstExcretionType
)


@admin.register(MilkRecord)
class MilkRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'milk_type', 'amount', 'left_breast_minutes', 'right_breast_minutes', 'action_at', 'created_at')
    search_fields = ('child__name',)
    list_filter = ('milk_type', 'child')

@admin.register(ExcretionRecord)
class ExcretionRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'excretion_type', 'memo', 'action_at', 'created_at')
    search_fields = ('child__name',)
    list_filter = ('excretion_type', 'child')

@admin.register(MstMilkType)
class MstMilkTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order_id', 'created_at')
    search_fields = ('name',)

@admin.register(MstExcretionType)
class MstExcretionTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order_id', 'created_at')
    search_fields = ('name',)



