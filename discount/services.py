from django.utils import timezone
from rest_framework.exceptions import ValidationError

from cart.models import Cart
from discount.models import Discount


class BaseDiscountValidator:
    Exception = ValidationError

    @classmethod
    def validate(cls, discount: Discount, cart: Cart):
        raise NotImplementedError


class IsActiveValidator(BaseDiscountValidator):
    @classmethod
    def validate(cls, discount: Discount, cart: Cart, ):
        if discount.is_active:
            return True
        raise cls.Exception(
            {'message': 'code is not active'})


class MinCartPriceValidator(BaseDiscountValidator):
    @classmethod
    def validate(cls, discount: Discount, cart: Cart):
        if not discount.min_value:
            return True
        if discount.min_value:
            cart_total_price = cart.get_cart_price()
            discount_min_value = discount.min_value
            if cart_total_price >= discount_min_value:
                return True
        raise cls.Exception(
            {'message': f'The discount could only applied on carts with minimum price {discount.min_value} '})


class ExpDateValidator(BaseDiscountValidator):
    @classmethod
    def validate(cls, discount: Discount, cart: Cart):
        if not discount.exp_date:
            return True
        if discount.exp_date > timezone.now():
            return True
        raise cls.Exception(
            {'message': 'Discount is expired'})
