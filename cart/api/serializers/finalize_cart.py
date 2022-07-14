from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from account.models import Address
from cart.models import Cart
from discount.models import Discount
from discount.services import BaseDiscountValidator


class FinalizeCartSerializer(ModelSerializer):  # user should send id of address
    address = serializers.CharField(allow_null=False, allow_blank=False, required=True)
    discount = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    def validate_address(self, address_id):
        request = self.context.get('request')
        address = get_object_or_404(Address, user=request.user, id=address_id)
        return address

    def validate_discount(self, discount_code):
        cart: Cart = self.context.get('cart')
        discount = Discount.objects.filter(code=discount_code).first()
        if not discount:
            raise serializers.ValidationError({'message': 'your code is not correct'})
        for Validator in BaseDiscountValidator.__subclasses__():
            Validator.validate(discount, cart)
        return discount

    class Meta:
        model = Cart
        fields = (
            'address',
            'discount'
        )
