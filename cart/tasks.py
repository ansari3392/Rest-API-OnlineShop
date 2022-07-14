# celery task to change cart with step pending after 1 hour to cart with step canceled


# @shared_task
# def cart_cancel_pending(*args, **kwargs):
#     pk = kwargs['cart_pk']
#     cart = Cart.objects.get(pk=pk)
#     if cart.step == Cart.StepChoices.PENDING:
#         cart.step = Cart.StepChoices.CANCELED
#         cart.save()

