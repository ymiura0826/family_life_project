from django.urls import path
from .views.top import IkujiTopView
from .views.milk_register import MilkRegisterView
from .views.milk_list import MilkListView
from .views.milk_detail import MilkDetailView
from .views.excretion_register import ExcretionRecordRegisterView
from .views.excretion_list import ExcretionRecordListView
from .views.excretion_detail import ExcretionRecordDetailView


urlpatterns = [
    path('', IkujiTopView.as_view(), name='ikujikanri_top'),
    path('milk/register/<int:child_id>/', MilkRegisterView.as_view(), name='milk_register'),
    path('milk/list/<int:child_id>/', MilkListView.as_view(), name='milk_list'),
    path('milk/detail/<int:pk>/', MilkDetailView.as_view(), name='milk_detail'),
    path('excretion/register/<int:child_id>/', ExcretionRecordRegisterView.as_view(), name='excretion_register'),
    path('excretion/list/<int:child_id>/', ExcretionRecordListView.as_view(), name='excretion_list'),
    path('excretion/detail/<int:excretion_record_id>/', ExcretionRecordDetailView.as_view(), name='excretion_detail'),

]
