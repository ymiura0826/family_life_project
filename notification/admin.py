from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    NotificationLog,
    NotifySchedule, 
    MstNotifyMethod, 
    MstNotifyType,
)


@admin.register(NotifySchedule)
class NotifyScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'family', 'notify_type', 'notify_method', 'schedule_at', 'created_at')
    search_fields = ('family__family_authentication_id',)
    list_filter = ('family', 'schedule_at')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'family', 'notify_type', 'notify_method', 'success_flag', 'action_at')
    list_filter = ('notify_type', 'notify_method', 'success_flag')
    search_fields = ('notify_content', 'group_id')

@admin.register(MstNotifyMethod)
class MstNotifyMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order_id', 'created_at')
    search_fields = ('name',)

@admin.register(MstNotifyType)
class MstNotifyTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order_id', 'created_at')
    search_fields = ('name',)


