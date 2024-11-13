# pages/urls.py
from django.urls import path

from . import views
from .views import home, pinterest_auth, pin_publish, pinterest_access_token

urlpatterns = [
    path("", home, name="social_publish"),
    path('pinterest-auth', pinterest_auth, name='pinterest_auth'),
    path('pinterest-access_token', pinterest_access_token, name='pinterest-access_token'),
    path('pin_publish', pin_publish, name='pin_publish')
]
