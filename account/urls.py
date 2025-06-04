# account/urls.py
from django.urls import path
from .views.user_register import UserRegisterView
from .views.family_register import FamilyRegisterView
from .views.family_authentication import FamilyAuthenticationView
from .views.family_select import FamilySelectView
from account.views.top import top_view
from account.views.logout import LogoutView
from account.views.login import CustomLoginView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('register/family/register/', FamilyRegisterView.as_view(), name='family_register'),
    path('register/family/authentication/', FamilyAuthenticationView.as_view(), name='family_authentication'),
    path('register/family/', FamilySelectView.as_view(), name='family_select'),
    path('', top_view, name='top'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
