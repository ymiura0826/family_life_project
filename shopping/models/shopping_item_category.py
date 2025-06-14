from django.db import models
from common.models.timestamped import TimeStampedModel

class MstShoppingItemCategory(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    order_id = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'm_shopping_item_category'