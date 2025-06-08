# shopping/urls.py

from django.urls import path
from shopping.views.top import ShoppingTopView
from shopping.views.item_edit import ShoppingItemUpdateView
from shopping.views.template_edit import ShoppingTemplateEditView

urlpatterns = [
    path('top/', ShoppingTopView.as_view(), name='shopping_top'),
    path('item/<int:pk>/edit/', ShoppingItemUpdateView.as_view(), name='shopping_item_edit'),
    path('template/<int:family_id>/',ShoppingTemplateEditView.as_view(),name='shopping_template_edit'),
]
