from django.urls import path, include
app_name = 'shipping'

urlpatterns = [
    path('shipping/', include('shipping.api.urls'))
]
