# pages/urls.py
from django.urls import path

from . import views
from .views import result_details, search, quarterly_plan, trending, display_quarter

urlpatterns = [
    path("details/<seed_keyword>", result_details, name="result_details"),
    path("search", search, name="search"),
    path("trending", trending, name="trending"),
    path("quarter", display_quarter, name="display_quarter"),
    path("<int:quarter>", display_quarter, name="display_quarter"),
    path("<int:quarter>/<int:month>", display_quarter, name="display_quarter")
]
