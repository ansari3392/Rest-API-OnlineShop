from typing import Union

from django.conf import settings
from django.db import models
from django.db.models import F, Sum, Prefetch, QuerySet
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from cart.utils import is_between
from discount.models import Discount
from product.models import Product
from shipping.models import Shipping

User = settings.AUTH_USER_MODEL


class CartManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(step=Cart.StepChoices.INITIAL)

    def get_annotated(self) -> QuerySet['Cart']:
        from cart.models import OrderItem
        orderitems = OrderItem.objects.annotate(
            product_price=F('product__base_price') + F('product__profit_price'),
        ).annotate(
            order_line_price=F('product_price') * F('quantity')
        ).select_related('product')
        prefetch = Prefetch('orderitems', queryset=orderitems)
        qs = self.get_queryset().prefetch_related(prefetch)
        return qs


class OrderManager(models.Manager):
    def get_queryset(self):

        return super().get_queryset().exclude(step=Cart.StepChoices.INITIAL)


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        db_index=True,
    )

    class StepChoices(models.TextChoices):
        INITIAL = 'initial', 'سبد خرید اولیه'
        PENDING = 'pending', 'در انتظار پرداخت'
        PAID = 'paid', 'پرداخت شده'
        DELIVERED = 'delivered', 'ارسال شده'
        CANCELED = 'canceled', 'کنسل شده'

    step = models.CharField(
        'step',
        max_length=9,
        default=StepChoices.INITIAL,
        choices=StepChoices.choices,
        db_index=True,
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )
    finalized_at = models.DateTimeField(
        auto_now=True
    )
    shipping = models.ForeignKey(
        'shipping.Shipping',
        on_delete=models.SET_NULL,
        related_name='carts',
        null=True,
    )
    shipping_price = models.PositiveIntegerField(
        default=0,
        help_text="این فیلد به صورت اتوماتیک بعد از نهایی شدن سفارش پر میشود."
    )
    discount = models.ForeignKey(
        'discount.Discount',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    discount_price = models.PositiveIntegerField(
        default=0,
        help_text="این فیلد به صورت اتوماتیک بعد از نهایی شدن سفارش پر میشود."
    )
    receiver_address = models.TextField(
        null=True,
        blank=True,
    )
    delivered_at = models.DateField(
        null=True,
        blank=True
    )
    objects = CartManager()

    class Meta:
        ordering = ('-finalized_at',)
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f'{self.user} - {self.step}'

    def get_cart_price(self):
        # get annotated field
        try:
            total_price = sum([orderitem.order_line_price for orderitem in self.orderitems.all()])
        except AttributeError:
            aggregated_price: dict = self.orderitems.annotate(
                total_price=(F('product__base_price') + F('product__profit_price')) * F('quantity'),
            ).aggregate(
                total=Sum('total_price')
            )
            total_price = aggregated_price['total'] or 0
        return total_price

    def add_item(self, product: Product, quantity: int):
        if self.orderitems.filter(product_id=product.id).exists():
            self.orderitems.filter(product_id=product.id).update(quantity=F('quantity') + quantity)
        else:
            self.orderitems.create(
                product=product,
                quantity=quantity
            )

    def allowed_to_finalize(self, raise_exception=True) -> bool:
        message = None
        if not self.orderitems.exists():
            message = 'your basket is empty'
        else:
            if self.get_cart_price() < settings.MINIMUM_CART_PRICE_TO_FINALIZE:
                message = 'you can only finalize your cart if your total price is greater than ' + str(
                    settings.MINIMUM_CART_PRICE_TO_FINALIZE)
        start_time = settings.FINALIZE_CART_PERIOD.get('start')
        end_time = settings.FINALIZE_CART_PERIOD.get('end')
        if not is_between(timezone.now().time(), start_time, end_time):
            message = 'we are closed now.you can only finalize your cart between ' + str(
                settings.FINALIZE_CART_PERIOD['start']) + ' and ' + str(settings.FINALIZE_CART_PERIOD['end'])
        if message:
            if raise_exception:
                raise ValidationError({'message': message})
            return False
        return True

    def finalize(self, address, discount: Union[Discount, None]):
        for item in self.orderitems.all():
            item.price = item.product.get_price()
            item.save()

        self.step = Cart.StepChoices.PENDING
        self.receiver_address = address.get_full_address()
        if discount:
            self.discount = discount
            self.discount_price = discount.calculate_discount_amount(discount, self)

        shipping: Shipping = self.get_shipping()
        self.shipping = shipping
        self.shipping_price = shipping.price

        self.finalized_at = timezone.now()
        self.save()

    def get_shipping(self) -> Shipping:
        if self.orderitems.filter(product__is_fragile=True).exists():
            shipping = Shipping.objects.filter(type='express').first()
        else:
            shipping = Shipping.objects.filter(type='regular').first()
        return shipping


class Order(Cart):
    class Meta:
        proxy = True
    objects = OrderManager()

    def get_order_price(self):
        total_price = self.orderitems.annotate(order_price=F('price') * F('quantity')).aggregate(
            total=Sum('order_price'))
        return total_price['total'] if total_price['total'] else 0

    def get_order_price_after_discount(self):
        return self.get_order_price() - self.discount_price

    def get_shipping_price(self):
        return self.shipping.price

    def get_order_price_with_shipping(self):
        return self.get_order_price_after_discount() + self.shipping_price
