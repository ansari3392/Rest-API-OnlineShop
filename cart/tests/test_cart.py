from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from cart.models import Cart, OrderItem
from cart.tests.service import create_user
from product.models import Product

User = get_user_model()


class CartTest(APITestCase):

    def setUp(self):
        self.user = create_user('mahsa', 'mah61700250185')
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
            profit_price='5000'
        )
        refresh = RefreshToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        self.cart: Cart = Cart.objects.get_annotated().filter(user=self.user).first()

    def test_get_cart_success(self):
        self.cart.orderitems.create(product=self.product1)
        self.cart.orderitems.create(product=self.product2)
        self.cart.refresh_from_db()
        url = reverse('cart:api:cart')
        response = self.client.get(url)
        self.cart.refresh_from_db()
        cart_price = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('orderitems')), self.cart.orderitems.count())
        self.assertEqual(response.data.get('orderitems')[0].get('product_title'), self.product1.title)
        self.assertEqual(response.data.get('cart_price'), cart_price)

    def test_add_to_cart_success(self):
        self.assertEqual(self.cart.orderitems.count(), 0)
        self.assertEqual(self.cart.get_cart_price(), 0)
        url = reverse('cart:api:add_or_remove_from_cart')
        data = {
            'product': self.product1.id,
            'quantity': 2
        }
        response = self.client.post(url, data)
        self.cart.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Product added successfully')
        cart_price = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price)

    def test_add_existed_product_to_cart_success(self):
        self.cart.orderitems.create(product=self.product1)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.orderitems.count(), 1)
        cart_price_before_adding = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price_before_adding)
        url = reverse('cart:api:add_or_remove_from_cart')
        data = {
            'product': self.product1.id,
            'quantity': 2
        }
        self.cart.refresh_from_db()
        response = self.client.post(url, data)
        cart_price = sum([3 * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_items_count = self.cart.orderitems.count()
        self.assertEqual(order_items_count, 1)
        cart_price = sum([3 * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price)

    def test_add_another_product_success(self):
        self.cart.orderitems.create(product=self.product1)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.orderitems.count(), 1)
        cart_price_before_adding = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price_before_adding)
        url = reverse('cart:api:add_or_remove_from_cart')
        data = {
            'product': self.product2.id,
        }
        self.cart.refresh_from_db()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.cart.orderitems.count(), 2)
        cart_price = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price)

    def test_remove_order_item_success(self):
        order_item = OrderItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.orderitems.count(), 1)
        cart_price_before_removing = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price_before_removing)
        url = reverse('cart:api:add_or_remove_from_cart')
        data = {
            'order_item': order_item.id,
        }
        self.cart.refresh_from_db()
        cart_price = sum([item.quantity * item.product.get_price() for item in self.cart.orderitems.all()])
        self.assertEqual(self.cart.get_cart_price(), cart_price)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        order_items_count = self.cart.orderitems.count()
        self.assertEqual(order_items_count, 0)
        self.assertEqual(self.cart.get_cart_price(), 0)

    def test_decrement_order_item_success(self):
        pass

    def test_increment_order_item_success(self):
        pass
