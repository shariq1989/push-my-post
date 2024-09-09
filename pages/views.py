# pages/views.py
from django.shortcuts import render, redirect


def index(request):
    if request.user.is_authenticated:
        # Redirect logged-in users to /scan/home
        return redirect('site_scan')  # Ensure 'site_scan' is the correct URL name for /scan/home
    return render(request, "home.html")


def privacy(request):
    return render(request, "privacy_policy.html")


def about(request):
    return render(request, "about.html")


def pin_rss_guide(request):
    return render(request, "blog/tutorials/pin_rss_guide.html")


def blog_improvement(request):
    return render(request, "blog/blog-improvement/blog-improvement.html")


def fcp(request):
    return render(request, "blog/blog-improvement/understanding_first_contentful_paint.html")


def resources(request):
    return render(request, "blog/resources.html")


def tutorials(request):
    return render(request, "blog/tutorials/tutorials.html")


def blog_audit(request):
    return render(request, "audits/blog_audit.html")
