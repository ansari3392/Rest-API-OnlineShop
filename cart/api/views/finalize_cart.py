from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import Address
from cart.api.serializers.finalize_cart import FinalizeCartSerializer
from cart.models import Cart
from discount.models import Discount


class FinalizeCartAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, *args, **kwargs):
        cart: Cart = Cart.objects.get_annotated().filter(user=self.request.user).first()
        cart.allowed_to_finalize(raise_exception=True)

        serializer = FinalizeCartSerializer(
            data=self.request.data,
            context={
                'request': self.request,
                'cart': cart
            })
        serializer.is_valid(raise_exception=True)
        address: Address = serializer.validated_data.get('address')
        discount: Discount = serializer.validated_data.get('discount')
        cart.finalize(address, discount)

        Cart.objects.create(user=self.request.user, step='initial')

        status_code = status.HTTP_200_OK
        response = {
            'message': 'finalized',
            'payment_url': 'https://google.com'
        }

        return Response(
            data=response,
            status=status_code
        )
