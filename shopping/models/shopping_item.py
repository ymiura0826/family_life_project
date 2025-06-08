from django.db import models
from django.contrib.auth.hashers import make_password
from common.models.timestamped import TimeStampedModel
from account.models.user import CustomUser
from account.models.family import Family
from .shopping_item_category import MstShoppingItemCategory


class ShoppingItem(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    shopping_item_category = models.ForeignKey(MstShoppingItemCategory,on_delete=models.SET_NULL, null=True, blank=False, related_name='shopping_items')
    item_name = models.CharField(max_length=200)
    memo = models.CharField(max_length=200)
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='shopping_items')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='shopping_items')
    completion_flag = models.BooleanField(null=False, blank=False)    

    def __str__(self):
        return self.item_name

    class Meta:
        db_table = 't_shopping_item'