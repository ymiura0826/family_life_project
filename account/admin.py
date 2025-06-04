from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    Family, 
    Child, 
    NotificationSetting, 
    MstSex
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # 表示カラム
    list_display = ('username', 'email', 'family', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'family')

    # 編集画面の構成（fieldsets）
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('family',)}),
    )

    # ユーザー作成画面の構成（add_fieldsets）
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('family',)}),
    )

    search_fields = ('username', 'email', )
    ordering = ('username',)

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('family_id', 'family_authentication_id', 'created_at', 'deleted_at')
    search_fields = ('family_authentication_id',)

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('child_id', 'name', 'birth_date', 'sex', 'family', 'created_at')
    search_fields = ('name',)
    list_filter = ('sex', 'family')

@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'family', 'notify_method', 'enable_notify_flag', 'created_at')
    search_fields = ('family__family_authentication_id',)
    list_filter = ('enable_notify_flag', 'family')

@admin.register(MstSex)
class MstSexAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'order_id', 'created_at')
    search_fields = ('name',)


