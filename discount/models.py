from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Discount(models.Model):
    percentage = models.FloatField(
        blank=True,
        null=True,
        help_text='درصد تخفیف',
    )
    constant = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='مقدار ثابت تخفیف اگر درصدی نبود'
    )
    ceil = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='سقف تخفیف (اگر تخفیف به صورت درصدی است این فیلد را پر کنید)'
    )
    min_value = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='حداقل مقدار خرید تا بتواند از کد تخفیف استفاده کند'
    )
    code = models.CharField(
        max_length=20,
        unique=True
    )

    start_date = models.DateTimeField(
        default=timezone.now
    )
    exp_date = models.DateTimeField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

    def __str__(self):
        return f'{self.percentage}%' if self.percentage else f'{self.constant}تومان'

    def save(self, *args, **kwargs):
        if all([self.percentage, self.constant]):
            raise ValidationError('you should send discount with percent or constant')
        if not any([self.percentage, self.constant]):
            raise ValidationError('you should send discount with percent or constant')
        super().save(*args, **kwargs)

    def estimate_discount_type(self):
        return 'percentage' if self.percentage else 'constant'

    def calculate_discount_amount(self, discount, cart):
        type_ = self.estimate_discount_type()

        if type_ == 'percentage':
            discount_amount = cart.get_cart_price() * discount.percentage // 100
        else:
            discount_amount = discount.constant

        # check cart total price is greater than minimum price
        if discount.ceil:
            if discount_amount > discount.ceil:
                discount_amount = discount.ceil
        return discount_amount

    def apply_discount(self, cart):
        return cart.get_cart_price() - self.calculate_discount_amount(self, cart)
