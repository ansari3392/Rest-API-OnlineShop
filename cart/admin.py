from django.contrib import admin

from cart.models import Cart, OrderItem
from cart.models.cart import Order


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created')
    list_filter = ('user', 'created')
    inlines = [OrderItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]


