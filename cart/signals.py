from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from cart.models.cart import Cart

User = get_user_model()

@receiver(post_save, sender=User)
def create_initial_cart(sender, created, instance, **kwargs):
    if created:
        Cart.objects.create(user=instance, step="initial")




