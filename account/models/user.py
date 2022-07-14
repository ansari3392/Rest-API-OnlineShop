from django.contrib.auth.models import AbstractUser

from cart.models import Cart


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def get_initial_cart(self):
        return Cart.objects.filter(user=self, step='initial').first()
