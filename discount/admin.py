from django.contrib import admin
from django.core.exceptions import ValidationError

from discount.models import Discount


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'exp_date', 'min_value')
    list_filter = ('start_date', 'exp_date', 'min_value')

    # def save_model(self, request, obj, form, change):
    #     percentage = obj.percentage
    #     constant = obj.constant
    #     if all([percentage, constant]):
    #         raise ValidationError('you should send discount with percent or constant')
    #     if not any([percentage, constant]):
    #         raise ValidationError('you should send discount with percent or constant')
    #     super().save_model(request, obj, form, change)

    # def has_add_permission(self,request, *args, **kwargs):
    #     super(DiscountAdmin, self).has_add_permission(request)
    #     has_permission = True
    #     if self.model.objects.exists():
    #         has_permission = False
    #     return has_permission
    #
    # def has_change_permission(self, *args, **kwargs):
    #     return True
    #
    # def has_delete_permission(self, *args, **kwargs):
    #     return True
