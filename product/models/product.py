from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    title = models.CharField(
        max_length=255,
    )
    subtitle = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    slug = models.SlugField(
        blank=True,
        db_index=True,
        unique=True
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    image = models.ImageField(
        null=True,
        blank=True
    )
    is_fragile = models.BooleanField(default=False)
    base_price = models.PositiveBigIntegerField()
    profit_price = models.PositiveBigIntegerField(
        default=0
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_price(self):
        return self.base_price + self.profit_price

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id, self.slug])

