from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import CustomUser, Profile, Address


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'is_superuser')
    list_filter = ('first_name',)
    inlines = [ProfileInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city',)
    list_filter = ('user', 'city',)
