from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from cart.models import Cart, OrderItem
from utils.func import PersianDateTime


class OrderItemSerializer(ModelSerializer):
    product_title = SerializerMethodField()

    @staticmethod
    def get_product_title(obj):
        return obj.product.title if obj.product.title else ''

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product_title',
            'price',
            'quantity',

        )
        read_only_fields = ('id',)


class OrderListSerializer(ModelSerializer):
    full_name = SerializerMethodField()
    order_price = SerializerMethodField()
    order_price_after_discount = SerializerMethodField()
    order_price_with_shipping = SerializerMethodField()
    finalized_at = SerializerMethodField()

    @staticmethod
    def get_full_name(obj):
        return obj.user.get_full_name() if obj.user.get_full_name() else ''

    @staticmethod
    def get_order_price(obj):
        return obj.get_order_price() if obj.get_order_price() else 0

    @staticmethod
    def get_order_price_after_discount(obj):
        return obj.get_order_price_after_discount()

    @staticmethod
    def get_order_price_with_shipping(obj):
        return obj.get_order_price_with_shipping() if obj.get_order_price_with_shipping() else 0

    @staticmethod
    def get_finalized_at(obj):
        return PersianDateTime(obj.finalized_at)

    class Meta:
        model = Cart
        fields = (
            'id',
            'user',
            'full_name',
            'step',
            'order_price',
            'discount_price',
            'order_price_after_discount',
            'shipping_price',
            'order_price_with_shipping',
            'finalized_at',
            'paid_at',
        )
        read_only_fields = ('id', 'paid_at')


class OrderRetrieveSerializer(ModelSerializer):
    orderitems = OrderItemSerializer(many=True)
    finalized_at = SerializerMethodField()
    order_price = SerializerMethodField()
    order_price_after_discount = SerializerMethodField()
    order_price_with_shipping = SerializerMethodField()

    @staticmethod
    def get_finalized_at(obj):
        return PersianDateTime(obj.finalized_at)

    @staticmethod
    def get_order_price(obj):
        return obj.get_order_price() if obj.get_order_price() else 0

    @staticmethod
    def get_order_price_after_discount(obj):
        return obj.get_order_price_after_discount()

    @staticmethod
    def get_order_price_with_shipping(obj):
        return obj.get_order_price_with_shipping() if obj.get_order_price_with_shipping() else 0

    class Meta:
        model = Cart
        fields = (
            'id',
            'step',
            'description',
            'orderitems',
            'finalized_at',
            'order_price',
            'discount_price',
            'order_price_after_discount',
            'shipping_price',
            'order_price_with_shipping',
        )
        read_only_fields = ('id', 'step')
