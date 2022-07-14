from django.contrib import admin

from shipping.models import Shipping


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'price')
    list_filter = ('price',)
