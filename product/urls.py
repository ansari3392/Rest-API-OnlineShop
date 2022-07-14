from django.urls import path, include
app_name = 'product'

urlpatterns = [
    path('', include('product.api.urls'))
]
