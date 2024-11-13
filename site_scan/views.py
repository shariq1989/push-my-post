from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
import json
# from PIL import Image, ImageFont, ImageDraw
# import praw
from environs import Env
from .service import sanitize_url, parse_sitemap, fetch_sites, fetch_trending_posts, find_trending_blog_posts, \
    save_site
from social_publish.service import pinterest_login, get_pinterest_user_data, create_board
import sys
from .models import Site, BlogPost
from social_publish.models import PinUser

env = Env()
env.read_env()  # read .env file, if it exists


#
# reddit = praw.Reddit(
#     client_id=env("PRAW_CLIENT_ID"),
#     client_secret=env("PRAW_CLIENT_SECRET"),
#     password=env("PRAW_PASSWORD"),
#     user_agent=env("PRAW_USER_AGENT"),
#     username=env("PRAW_USERNAME"),
# )
#


def home(request):
    sites = fetch_sites(request.user)
    context = {"sites": sites}
    return render(request, "scan/home.html", context)


def remove_site(request, site_id):
    if request.method == 'POST':
        site = get_object_or_404(Site, id=site_id)
        site.delete()
        messages.success(request, f"Removed site: {site.name}")
    return redirect('site_scan')


def update_boards_list(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest("User is not authenticated")

    try:
        pin_user = PinUser.objects.get(user=request.user)
    except PinUser.DoesNotExist:
        return HttpResponseBadRequest("PinUser entry not found for the logged-in user.")

    if pin_user.access_token:
        # boards = get_pinterest_user_data(pin_user)
        boards = [
            {'name': 'test'}
        ]
        return JsonResponse({"boards": boards})

    return HttpResponseBadRequest("No access token found.")


def scan_submit(request):
    selected_posts_ids = request.POST.getlist('selected_pages')
    selected_posts = BlogPost.objects.filter(pk__in=selected_posts_ids)
    print(f"User selected posts {selected_posts}")
    request.session['posts_for_pinning'] = selected_posts_ids
    # TODO uncomment
    pin_user, created = PinUser.objects.get_or_create(user=request.user)
    if pin_user.access_token:
        boards = get_pinterest_user_data(pin_user)
        # pass
    else:
        return pinterest_login()
        # pass
    # boards = [
    #     {'name': 'Delicious Desserts'},
    #     {'name': 'Healthy Recipes'},
    #     {'name': 'Quick and Easy Meals'},
    #     {'name': 'Vegetarian Delights'},
    #     {'name': 'Gourmet Cooking'}
    # ]
    context = {
        'posts': selected_posts,
        'boards': boards,
    }
    return render(request, 'social_publish/pin_publish.html', context)


def create_board_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get("title", "")
            description = data.get("description", "")
            if not title or not description:
                return HttpResponseBadRequest("Name and description are required")
            if not request.user.is_authenticated:
                return HttpResponseBadRequest("User is not authenticated")
            try:
                pin_user = PinUser.objects.get(user=request.user)
            except PinUser.DoesNotExist:
                return HttpResponseBadRequest("PinUser entry not found for the logged-in user.")
            create_board(name=title, description=description, pin_user=pin_user)

            # Respond with JSON if successful
            return JsonResponse({"message": "Board created successfully"})
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    else:
        return HttpResponseBadRequest("Only POST requests are allowed")


def search_submit(request, site_id):
    # Get the search query from the form
    search_query = request.GET.get('query')

    # Get the search option (title, description, both)
    search_option = request.GET.get('search_option', 'both')

    blog_posts = BlogPost.objects.filter(site__pk=site_id)

    # Check the search option and apply filters
    if search_query:
        if search_option == 'title':
            blog_posts = blog_posts.filter(title__icontains=search_query)
        elif search_option == 'description':
            blog_posts = blog_posts.filter(description__icontains=search_query)
        elif search_option == 'both':
            blog_posts = blog_posts.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
    site = Site.objects.get(pk=site_id)
    context = {
        'site': site,
        'site_id': site_id,
        'blog_posts': blog_posts,
        'blog_posts_count': len(blog_posts)

    }
    return render(request, 'scan/scan.html', context)


def site_blog_posts(request, site_id):
    site = Site.objects.get(pk=site_id)
    blog_posts = BlogPost.objects.filter(site=site).order_by('-date_modified')
    context = {
        'site': site,
        'site_id': site_id,
        'blog_posts': blog_posts,
        'blog_posts_count': len(blog_posts)
    }
    return render(request, 'scan/scan.html', context)


def get_site_trending_posts(request, site_id):
    site = Site.objects.get(pk=site_id)
    # Fetch quarterly and daily trend candidates
    trending_kw = fetch_trending_posts()
    blog_posts = find_trending_blog_posts(site, trending_kw)
    context = {
        'site': site,
        'site_id': site_id,
        'blog_posts': blog_posts,
        'blog_posts_count': len(blog_posts)
    }
    return render(request, 'scan/scan.html', context)


def get_site_recent_posts(request, site_id):
    site = Site.objects.get(pk=site_id)
    blog_posts = BlogPost.objects.filter(site=site).order_by('-date_modified')[:10]
    context = {
        'site': site,
        'site_id': site_id,
        'blog_posts': blog_posts,
        'blog_posts_count': len(blog_posts)

    }
    return render(request, 'scan/scan.html', context)


def submit_site(request):
    # TODO: handle URLs
    site = request.POST.get("url_input", "")
    print("Received site", site)
    site = sanitize_url(site)
    print("Converted to fully qualified URL", site)
    # TODO: Handle all sitemaps
    # TODO: Handle YOAST sitemap
    try:
        save_site(site, request)
    except ValueError as error:
        print('Error processing URL')
        print(error)
    # TODO: post_to_twitter(posts)
    # TODO: post_to_pinterest(posts)
    # TODO: post_to_reddit(posts)
    return home(request)


def post_to_reddit(posts):
    for post in posts:
        print('Posting to sub', post)
        post_to_subreddit(title=post['post_title'], image=post['image_path'], comment=post['post_desc'],
                          subreddit="jamilghar", url=post['url'])


def post_to_subreddit(title, image, comment, subreddit, url, calories=None):
    title = "[Recipe in Comments] " + title
    if subreddit in ['1200isplentyketo', '1200isplenty']:
        if not calories:
            print('No calories provided')
            return False
        title = title + " - " + calories + " calories/serving"
    try:
        resp = reddit.subreddit(subreddit).submit_image(title, image)
        print("Submitted to ", subreddit, resp.id, resp.created_utc, resp.url)
        if resp.id:
            comment_on_post(resp.id, comment, url)
    except Exception as e:
        print("Submitted to ", subreddit, title, image)
        print(e)
        pass  # keep posting


def comment_on_post(post_id, comment, url):
    submission = reddit.submission(post_id)
    comment = comment + '\n\n **Link to Full Recipe ' \
                        'along with process pictures, garnishes, serving suggestions, leftover instructions, etc)**' \
                        '\n\n [**' + url + '**](' + url + ')'
    comment_resp = submission.reply(comment)
    print("Commented on ", comment_resp, comment_resp.permalink)
