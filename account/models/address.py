from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='address'
    )
    province = models.CharField(
        max_length=255,
        null=True,
    )
    city = models.CharField(
        max_length=255,
        null=True,
    )
    address = models.CharField(
        max_length=500,
        null=True,

    )

    zip_code = models.IntegerField(
        null=True,
    )

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.user.username

    def get_full_address(self) -> str:
        return self.province + '' + self.city + '' + self.address + str(self.zip_code)
