import logging
import requests
from environs import Env
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from .models import Site, BlogPost
import re
from django.utils import timezone
from django.db.models import Count
from trends.service import get_this_quarter_and_month, search_data_for_month
from trends.models import Trending
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

env = Env()
env.read_env()  # read .env file, if it exists


def sanitize_url(url):
    if "https" not in url:
        return "https://" + url
    return url


def fetch_page_content(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url, headers=headers)
    response = urlopen(req)
    return response.read().decode('utf8')


def fetch_and_parse_sitemap(sitemap_url, headers):
    req = Request(sitemap_url, headers=headers)
    try:
        response = urlopen(req)
        sitemap_xml = BeautifulSoup(response, 'xml')
        return sitemap_xml
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return None


def extract_metadata(soup):
    title = soup.find("meta", property="og:title")
    desc = soup.find("meta", attrs={'name': "description"})

    if title and title.get("content") and desc and desc.get("content"):
        return title["content"], desc["content"]
    else:
        return None, None


def extract_featured_image_url(soup):
    featured_image_element = soup.find('meta', property='og:image')
    if featured_image_element and featured_image_element.get('content'):
        return featured_image_element['content']
    else:
        return None


def save_site_info(site_name, site_url, user):
    current_datetime = timezone.now()
    defaults = {'name': site_name, 'last_scan': current_datetime, 'user': user}
    site, created = Site.objects.update_or_create(url=site_url, defaults=defaults)
    return site


def save_blog_post(site, post_data):
    blog_post = BlogPost(
        site=site,
        title=post_data['post_title'],
        description=post_data['post_desc'],
        url=post_data['url'],
        featured_image_url=post_data['image_url'],
        date_modified=post_data['last_updt'],
    )

    # Add pin_image_url to the blog_post if it exists in post_data
    if 'pin_image_url' in post_data:
        blog_post.pin_image_url = post_data['pin_image_url']

    # Set other fields here if needed

    blog_post.save()


def fetch_sitemap_index(site_url, headers):
    sitemap_index_url = f"{site_url}/sitemap.xml"
    req = Request(sitemap_index_url, headers=headers)
    try:
        response = urlopen(req)
        xml = BeautifulSoup(response, 'xml')
        return xml
    except Exception as e:
        print(f"Error fetching sitemap index: {e}")
        return None


def extract_site_name(soup):
    title_element = soup.find('title')
    if title_element:
        site_name = title_element.get_text(strip=True).replace("XML Sitemap - ", "")
    else:
        site_name = None

    return site_name


def extract_pinterest_image_url(post_soup):
    # Find the Pinterest image URL in the HTML structure
    pinterest_button = post_soup.find('a', class_='wprm-recipe-pin')
    if pinterest_button:
        image_url = pinterest_button.get('data-media')
        return image_url
    else:
        return None


def parse_individual_sitemap(site, sitemap_xml):
    if sitemap_xml is None:
        return

    posts = []
    urls = sitemap_xml.find_all('url')

    for index, post in enumerate(urls):
        url_element = post.find('loc')
        lastmod_element = post.find('lastmod')

        if url_element and lastmod_element:
            url = url_element.get_text(strip=True)
            last_updt = lastmod_element.get_text(strip=True)

            page_content = fetch_page_content(url)
            post_soup = BeautifulSoup(page_content, 'html.parser')
            post_title, post_desc = extract_metadata(post_soup)
            image_url = extract_featured_image_url(post_soup)  # Fetch the featured image URL
            pin_image_url = extract_pinterest_image_url(post_soup)  # Fetch the Pinterest image URL

            if post_title and post_desc and image_url:
                post_data = {
                    'url': url,
                    'last_updt': last_updt,
                    'image_url': image_url,
                    'post_title': post_title,
                    'post_desc': post_desc
                }

                # Add pin_image_url to post_data if it exists
                if pin_image_url:
                    post_data['pin_image_url'] = pin_image_url

                posts.append(post_data)
                save_blog_post(site, post_data)  # Save the blog post
                if (index + 1) % 25 == 0:
                    logger.info(f"Parsing progress: {index + 1} posts parsed")

    return posts


def parse_sitemap(site_url, request, stop=False):
    headers = {'User-Agent': 'Mozilla/5.0'}
    # For setting site title
    logger.info(f"Fetching site home page for {site_url}")
    site_home_page_content = fetch_page_content(site_url)
    if not site_home_page_content:
        logger.error('Failed to fetch site home page')
        return []
    site_home_soup = BeautifulSoup(site_home_page_content, 'html.parser')
    site_name = extract_site_name(site_home_soup)
    logger.info(f"Site name extracted: {site_name}")

    site = save_site_info(site_name, site_url, request.user)  # Save site information
    logger.info(f"Site information saved: {site}")

    sitemap_index_xml = fetch_sitemap_index(site_url, headers)
    if sitemap_index_xml is None:
        logger.error('No sitemap found')
        return []

    sitemap_urls = sitemap_index_xml.find_all('loc')
    all_posts = []
    for index, sitemap_url_element in enumerate(sitemap_urls):
        sitemap_url = sitemap_url_element.get_text(strip=True)
        if "post-sitemap" in sitemap_url:
            logger.info(f"Fetching and parsing individual sitemap: {sitemap_url}")
            sitemap_xml = fetch_and_parse_sitemap(sitemap_url, headers)
            posts = parse_individual_sitemap(site, sitemap_xml)
            all_posts.extend(posts)
            if stop and len(all_posts) >= 5:
                logger.info("Parsing stopped due to 'stop' flag")
                break
            if (index + 1) % 25 == 0:
                logger.info(f"Parsing progress: {index + 1} sitemaps parsed")
    logger.info(f"Total posts parsed: {len(all_posts)}")

    return all_posts


def fetch_sites(user):
    sites = Site.objects.filter(user=user).annotate(blog_posts_count=Count('blogpost'))

    site_data = []
    for site in sites:
        site_info = {
            "site": site,
            "blog_posts_count": site.blog_posts_count,
        }
        site_data.append(site_info)

    return site_data


def fetch_trending_posts():
    quarter, month = get_this_quarter_and_month()
    month_data = search_data_for_month(None, str(month))
    how_res_keywords = set(keyword['keyword__keyword'] for keyword in month_data['how_res'])
    recipe_res_keywords = set(keyword['keyword__keyword'] for keyword in month_data['recipe_res'])

    # Combine both sets of keywords into a single set and make them unique
    all_trending_kw = set(how_res_keywords) | set(recipe_res_keywords)

    # Get daily trending keywords from the second method
    daily_trending_keywords = fetch_daily_trend_posts()

    # Merge daily trending keywords with the quarterly keywords and make them unique
    all_trending_kw |= daily_trending_keywords

    return all_trending_kw


def fetch_daily_trend_posts():
    # Get the current date
    current_date = datetime.now()

    # Calculate the date X weeks ago
    time_ago = current_date - timedelta(days=3)

    # Query to retrieve Trending keywords for batches created in the last X weeks
    trending_kw = Trending.objects.filter(
        batch__created_on__gte=time_ago
    )
    # Extract trending keywords from the query
    trending_keywords = set(entry.keyword.keyword.lower() for entry in trending_kw)
    return trending_keywords


def find_trending_blog_posts(site, trending_kw):
    # List to store matched blog posts
    matched_blog_posts = []

    blog_posts = BlogPost.objects.filter(site=site).order_by('-date_modified')

    # Step 3: Check each blog post for relevant keywords
    for post in blog_posts:
        # Tokenize the title and description, make them lowercase, and filter out short words
        excluded_words = ["recipe", "long", "what", "cook", "best", "easy"]  # Add words to exclude here
        title_words = [word.lower() for word in post.title.split() if
                       len(word) > 3 and word.lower() not in excluded_words]

        # description_words = [word.lower() for word in post.description.split() if len(word) > 3]

        # Split the long-tail keywords into individual words
        individual_keywords = [keyword.lower() for long_keyword in trending_kw for keyword in long_keyword.split()]
        # Count the number of relevant keywords in title and description
        matching_keywords = [word for word in title_words if word in individual_keywords]
        # description_matches = sum(1 for word in description_words if word in individual_keywords)
        # If at least 2/3 of the individual keywords are found in the title, consider it a match
        if len(matching_keywords) > 1:
            # print(f"Matching keywords {matching_keywords} in post: {post.title}")
            matched_blog_posts.append(post)

    return matched_blog_posts
