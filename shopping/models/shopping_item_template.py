from django.db import models
from django.contrib.auth.hashers import make_password
from common.models.timestamped import TimeStampedModel
from account.models.user import CustomUser
from account.models.family import Family
from .shopping_item_category import MstShoppingItemCategory


class ShoppingItemTemplate(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    shopping_item_category = models.ForeignKey(MstShoppingItemCategory,on_delete=models.SET_NULL, null=True, blank=False, related_name='item_templates')
    item_name = models.CharField(max_length=200)
    memo = models.CharField(max_length=200)
    family = models.ForeignKey(Family, to_field='family_id', on_delete=models.SET_NULL, null=True, blank=True, related_name='item_templates')
    order_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.item_name

    class Meta:
        db_table = 't_shopping_item_template'