from django.urls import path

from cart.api.views.cart import CartRetrieveAPIView, ManageCartAPIView
from cart.api.views.finalize_cart import FinalizeCartAPIView
from cart.api.views.order import OrderListAPIView, OrderRetrieveAPIView

app_name = 'api'

urlpatterns = [
    path('cart/', CartRetrieveAPIView.as_view(), name='cart'),
    path('manage-cart/', ManageCartAPIView.as_view(), name='add_or_remove_from_cart'),
    path('orders-list/', OrderListAPIView.as_view(), name='order_list'),
    path('order-detail/<pk>/', OrderRetrieveAPIView.as_view(), name='order_detail'),
    path('finalize-cart/', FinalizeCartAPIView.as_view(), name='finalize_cart'),
]
