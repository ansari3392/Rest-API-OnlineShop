from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from cart.models import Cart, Order
from cart.tests.service import create_user
from product.models import Product
from shipping.models import Shipping

User = get_user_model()


class OrdersTest(APITestCase):
    def setUp(self):
        self.user = create_user('mahsa', 'mah61700250185')
        self.shipping1 = Shipping.objects.create(
            type='regular',
            price=10000
        )
        self.shipping2 = Shipping.objects.create(
            type='express',
            price=20000
        )
        self.product1 = Product.objects.create(
            title="گوشی موبایل",
            description="توضیحات ندارد",
            is_fragile=True,
            base_price='3000000',
            profit_price='500000'
        )
        self.product2 = Product.objects.create(
            title="هندزفری",
            description="توضیحات ندارد",
            is_fragile=False,
            base_price='50000',
            profit_price='2000'
        )
        refresh = RefreshToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_get_empty_orders_list_success(self):
        url = reverse('cart:api:order_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 0)
        self.assertEqual(len(response.data.get('results')), 0)

    def test_get_orders_list_success(self):
        self.order1 = Order.order_objects.create(user=self.user, step=Cart.StepChoices.CANCELED)
        self.order1.orderitems.create(product=self.product1, quantity=3)
        self.order1.orderitems.create(product=self.product2, quantity=1)
        self.order2 = Order.order_objects.create(user=self.user, step=Cart.StepChoices.PAID)
        self.order2.orderitems.create(product=self.product2)
        url = reverse('cart:api:order_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('count'), 2)
        self.assertEqual(response.data.get('results')[0].get('step'), self.order2.step)
        self.assertEqual(response.data.get('results')[0].get('order_price'), self.order2.get_order_price())
        self.assertEqual(response.data.get('results')[0].get('discount_price'), self.order2.discount_price)
        self.assertEqual(response.data.get('results')[0].get('order_price_after_discount'),
                         self.order2.get_order_price_after_discount())
        self.assertEqual(response.data.get('results')[0].get('shipping_price'), self.order2.shipping_price)
        self.assertEqual(response.data.get('results')[0].get('order_price_with_shipping'),
                         self.order2.get_order_price_with_shipping())

    def test_get_orders_list_unauthorized_fail(self):
        self.client.logout()
        url = reverse('cart:api:order_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_order_detail_success(self):
        self.order = Order.order_objects.create(
            user=self.user,
            step=Cart.StepChoices.CANCELED,
            discount_price=100000,
            shipping_price=self.shipping2.price,)
        self.order.orderitems.create(product=self.product1, quantity=3, price=3500000)
        url = reverse('cart:api:order_detail', kwargs={'pk': self.order.id})
        response = self.client.get(url)
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('step'), 'canceled')
        self.assertEqual(response.data.get('description'), None)
        self.assertEqual(len(response.data.get('orderitems')), 1)
        self.assertEqual(response.data.get('orderitems')[0].get('product_title'), 'گوشی موبایل')
        self.assertEqual(response.data.get('orderitems')[0].get('quantity'), 3)
        self.order.refresh_from_db()
        self.assertEqual(response.data.get('order_price'), 3500000*3)
        self.assertEqual(response.data.get('discount_price'), self.order.discount_price)
        self.assertEqual(response.data.get('order_price_after_discount'), 3500000*3-100000)
        self.assertEqual(response.data.get('shipping_price'), self.shipping2.price)
        self.assertEqual(response.data.get('order_price_with_shipping'), 3500000*3-100000+self.shipping2.price)

    def test_get_order_detail_if_product_price_change(self):
        self.order = Order.order_objects.create(
            user=self.user,
            step=Cart.StepChoices.CANCELED,
            discount_price=100000,
            shipping_price=self.shipping2.price, )
        self.order.orderitems.create(product=self.product1, quantity=3, price=3500000)
        self.product1.base_price = '4000000'
        self.product1.save()
        url = reverse('cart:api:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('order_price'), 3500000*3)
        self.assertEqual(response.data.get('order_price_after_discount'), 3500000*3-100000)
        self.assertEqual(response.data.get('order_price_with_shipping'), 3500000*3-100000+self.shipping2.price)

    def test_get_orders_detail_unauthorized_fail(self):
        self.order = Order.order_objects.create(
            user=self.user,
            step=Cart.StepChoices.CANCELED,
            discount_price=100000,
            shipping_price=self.shipping2.price, )
        self.order.orderitems.create(product=self.product1, quantity=3, price=3500000)
        self.client.logout()
        url = reverse('cart:api:order_detail', kwargs={'pk': self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_detail_not_found_fail(self):
        url = reverse('cart:api:order_detail', kwargs={'pk': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
