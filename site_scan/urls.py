# pages/urls.py
from django.urls import path

from . import views
from .views import home, submit_site, scan_submit, remove_site, get_site_recent_posts, get_site_trending_posts, search_submit

urlpatterns = [
    path("", home, name="site_scan"),
    path("submit_site", submit_site, name="submit_site"),
    path("remove_site/<int:site_id>", remove_site, name="remove_site"),
    path('site/<int:site_id>/', views.site_blog_posts, name='site_blog_posts'),
    path('site/<int:site_id>/trending', views.get_site_trending_posts, name='get_site_trending_posts'),
    path('site/<int:site_id>/recent', views.get_site_recent_posts, name='get_site_recent_posts'),
    path("scan_submit", scan_submit, name="scan_submit"),
    path("search/<int:site_id>/", search_submit, name="search")
]
