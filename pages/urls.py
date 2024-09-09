# pages/urls.py
from django.urls import path

from . import views
from .views import index, privacy, about, pin_rss_guide, resources, tutorials, blog_audit, blog_improvement, fcp

urlpatterns = [
    path("", index, name="index"),
    path("privacy", privacy, name="privacy"),
    path("about", about, name="about"),
    path("resources", resources, name="resources"),
    path("blog_audit", blog_audit, name="blog_audit"),
    path("tutorials", tutorials, name="tutorials"),
    path("pin_rss_guide", pin_rss_guide, name="pin_rss_guide"),
    path("blog-improvement", blog_improvement, name="blog-improvement"),
    path("fcp", fcp, name="fcp")
]
