from django.urls import path
from .views import protected_profile_view

urlpatterns = [
  path('profile/', protected_profile_view, name='profile_view'),
]
