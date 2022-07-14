from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.api.serializers.cart import AddToCartSerializer, \
    RemoveFromCartSerializer, CartRetrieveSerializer
from cart.models.cart import Cart
from product.models import Product


class CartRetrieveAPIView(RetrieveAPIView):
    serializer_class = CartRetrieveSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        cart = Cart.objects.get_annotated().filter(user=self.request.user).first()
        return cart


class ManageCartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, *args, **kwargs):
        serializer = AddToCartSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        product: Product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')
        cart: Cart = self.request.user.get_initial_cart()
        cart.add_item(product, quantity)
        return Response(
            data={'message': 'Product added successfully'},
            status=status.HTTP_200_OK
        )

    def delete(self, *args, **kwargs):
        cart: Cart = self.request.user.get_initial_cart()
        serializer = RemoveFromCartSerializer(
            data=self.request.data,
            context={'cart': cart}
        )
        serializer.is_valid(raise_exception=True)
        order_item = serializer.validated_data.get('order_item')
        order_item.delete()
        return Response(
            data={'message': 'Removed'},
            status=status.HTTP_204_NO_CONTENT
        )



