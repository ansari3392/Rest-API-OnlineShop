from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from cart.models import OrderItem
from cart.models.cart import Cart
from product.models import Product


class CartOrderItemSerializer(ModelSerializer):
    product_title = serializers.CharField(source='product.title')
    product_price = serializers.IntegerField()
    order_line_price = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product_title',
            'product_price',
            'quantity',
            'order_line_price',
        )


class CartRetrieveSerializer(ModelSerializer):
    orderitems = CartOrderItemSerializer(many=True)
    cart_price = SerializerMethodField()

    @staticmethod
    def get_cart_price(obj: Cart) -> int:
        return obj.get_cart_price()

    class Meta:
        model = Cart
        fields = (
            'orderitems',
            'cart_price'
        )


class AddToCartSerializer(serializers.Serializer):  # user should send id of product
    product = serializers.CharField(allow_null=False, allow_blank=False, required=True)
    quantity = serializers.IntegerField(default=1)

    @staticmethod
    def validate_product(product_id):
        product = get_object_or_404(Product, id=product_id)
        return product


class RemoveFromCartSerializer(serializers.Serializer):  # user should send id of order_item
    order_item = serializers.CharField(allow_null=False, allow_blank=False, required=True)

    def validate_order_item(self, order_item_id):
        cart = self.context.get('cart')
        order_item = get_object_or_404(OrderItem, id=order_item_id, cart_id=cart.id)
        return order_item
