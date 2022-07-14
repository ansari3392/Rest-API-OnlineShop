from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.api.views.register import RegisterView

app_name = 'api'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('access/', TokenObtainPairView.as_view(), name='access'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
]
