from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from cart.models import Order


@shared_task
def cancel_pending_orders():
    expire: int = settings.CART_ORDER_EXPIRE_TIME
    orders = Order.objects.filter(
        step=Order.StepChoices.PENDING,
        finalized_at__lte=timezone.now() - timedelta(seconds=expire)
    )
    result = orders.update(step=Order.StepChoices.CANCELED)
    return result

