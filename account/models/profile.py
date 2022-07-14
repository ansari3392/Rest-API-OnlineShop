from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Profile(models.Model):

    class GenderChoices(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    gender = models.CharField(
        null=True,
        max_length=6,
        choices=GenderChoices.choices,
    )
    avatar = models.ImageField(
        null=True,
        blank=True
    )
    bio = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return self.user.username

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else ''
