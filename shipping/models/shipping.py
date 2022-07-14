from django.db import models


class Shipping(models.Model):
    class ShipmentChoices(models.TextChoices):
        REGULAR = 'regular', 'پست معمولی'
        EXPRESS = 'express', 'پست پیشتاز'

    type = models.CharField(
        'type',
        max_length=12,
        choices=ShipmentChoices.choices,
    )
    price = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Shipping"
        verbose_name_plural = "Shipping"

    def __str__(self):
        return self.type
