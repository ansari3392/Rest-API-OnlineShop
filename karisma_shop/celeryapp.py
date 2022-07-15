import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karisma_shop.settings')

celery_app = Celery('Karisma_shop')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')

celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'cancel-pending-orders': {
        'task': 'cart.tasks.cancel_pending_orders',
        'schedule': 30.0,
    },
}
celery_app.conf.timezone = 'Asia/Tehran'
