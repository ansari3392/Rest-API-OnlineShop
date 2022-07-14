from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

User = settings.AUTH_USER_MODEL


class OrderItem(models.Model):
    """
        Intermediary model of Cart and product
        Each cart can have several product
        and Each product could be in many carts
    """
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        db_index=True,
        related_name='orderitems'
    )
    cart = models.ForeignKey(
        'cart.Cart',
        on_delete=models.CASCADE,
        related_name='orderitems',
        db_index=True,
    )
    price = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        help_text='این فیلد در لحظه ی نهایی شدن سفارش، به صورت اتوماتیک ذخیره میشود'
    )
    quantity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        null=True
    )
    created = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'product "{self.product.title}" in cart "{self.cart.user}"'
