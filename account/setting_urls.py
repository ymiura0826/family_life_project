# account/setting_urls.py

from django.urls import path
from .views.family_detail import FamilyDetailView
from .views.family_pass_change import FamilyPassChangeView
from .views.family_line_token_change import FamilyLineTokenChangeView
from .views.user_detail import UserDetailView
from .views.user_pass_change import UserPasswordChangeView
from .views.notification_setting import NotificationSettingDetailView
from common.views.setting_complete import SettingCompleteView
from account.views.child_create import ChildCreateView
from account.views.child_update import ChildUpdateView
from account.views.child_delete import ChildDeleteView

urlpatterns = [
    path('family/detail/<int:pk>/', FamilyDetailView.as_view(), name='family_detail'),
    path('family/pass_change/', FamilyPassChangeView.as_view(), name='family_pass_change'),
    path('family/line_token_change/', FamilyLineTokenChangeView.as_view(), name='family_line_token_change'),
    path('user/detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('user/pass_change/', UserPasswordChangeView.as_view(), name='user_pass_change'),
    path('notification/', NotificationSettingDetailView.as_view(), name='notification_setting'),
    path('complete/', SettingCompleteView.as_view(), name='setting_complete'),
    path('family/children/register/', ChildCreateView.as_view(), name='child_create'),
    path('family/children/<int:pk>/', ChildUpdateView.as_view(), name='child_update'),
    path('family/children/<int:pk>/delete/', ChildDeleteView.as_view(), name='child_delete'),
]
