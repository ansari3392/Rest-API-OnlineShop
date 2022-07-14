from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from cart.api.serializers.order import OrderListSerializer, OrderRetrieveSerializer
from cart.models import Order


class OrderListAPIView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = (IsAuthenticated,)

    filterset_fields = (
        'created',
        'step',
    )

    def get_queryset(self):
        qs = Order.order_objects.filter(user=self.request.user).prefetch_related('orderitems')
        return qs


class OrderRetrieveAPIView(RetrieveAPIView):
    serializer_class = OrderRetrieveSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = Order.order_objects.filter(user=self.request.user).prefetch_related('orderitems')
        return qs
