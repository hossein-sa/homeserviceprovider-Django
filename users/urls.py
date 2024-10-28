from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import UserRegistrationView, ProfileView, SpecialistOnlyView, CustomerOnlyView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('specialists/', SpecialistOnlyView.as_view(), name='specialist-only'),
    path('customers/', CustomerOnlyView.as_view(), name='customers-only'),
    path('api-token-auth', obtain_auth_token, name='api-token-auth'),
]
