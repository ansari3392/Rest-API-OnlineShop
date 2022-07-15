from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import Address
from cart.models import Cart
from cart.tests.service import create_user
from discount.models import Discount
from product.models import Product
from shipping.models import Shipping

User = get_user_model()


class FinalizeCartTest(APITestCase):

    def setUp(self):
        self.user = create_user('mahsa', 'mah61700250185')
        self.address = Address.objects.create(
            user=self.user,
            province='Tehran',
            city="tehran",
            address='somewhere',
            zip_code=1234567890, )
        self.discount1 = Discount.objects.create(
            percentage=10,
            ceil=50000,
            min_value=200000,
            code='test',
            is_active=True,
        )
        self.discount2 = Discount.objects.create(
            constant=10,
            min_value=200000,
            code='test2',
            exp_date='2020-01-01',
            is_active=True,
        )
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
            base_price=3000000,
            profit_price=500000)
        self.product2 = Product.objects.create(
            title="هندزفری",
            description="توضیحات ندارد",
            is_fragile=False,
            base_price=20000,
            profit_price=1000
        )

        refresh = RefreshToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.cart: Cart = Cart.objects.get_annotated().filter(user=self.user).first()

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_success(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'finalized')

    @patch('cart.models.cart.is_between')
    def test_finalize_empty_cart_fail(self, mock_is_between):
        mock_is_between.return_value = True
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'your basket is empty')

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_when_cart_price_is_low_fail(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product2, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_when_shop_is_closed_fail(self, mock_is_between):
        mock_is_between.return_value = False
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_without_discount_code_success(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'finalized')

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_with_incorrect_discount_code_fail(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'testing'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['discount'].get('message'), 'your code is not correct')

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_with_expired_discount_code_fail(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product2, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test2'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_with_discount_when_cart_price_is_lower_than_discount_min_value_fail(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test2'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('cart.models.cart.is_between')
    def test_finalize_cart_without_address_fail(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('cart.models.cart.is_between')
    def test_change_cart_step_success(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.cart.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'finalized')
        self.assertEqual(self.cart.step, 'pending')

    @patch('cart.models.cart.is_between')
    def test_save_product_price_in_order_item_success(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.cart.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'finalized')
        order_item_price = self.cart.orderitems.first().price
        self.assertEqual(order_item_price, self.product1.get_price())

    @patch('cart.models.cart.is_between')
    def test_save_shipping_price_in_order_success(self, mock_is_between):
        mock_is_between.return_value = True
        self.cart.orderitems.create(product=self.product1, quantity=1)
        url = reverse('cart:api:finalize_cart')
        data = {
            'address': self.address.id,
            'discount': 'test'
        }
        response = self.client.post(url, data)
        self.cart.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'finalized')
        shipping_price = self.cart.shipping_price
        self.assertEqual(shipping_price, self.shipping2.price)
        self.assertEqual(self.cart.step, 'pending')

    @patch('cart.models.cart.is_between')
    def test_save_discount_price_in_order_success(self, mock_is_between):
        pass


