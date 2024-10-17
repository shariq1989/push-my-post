from django.shortcuts import render
from .service import request_pinterest, pinterest_login, get_pinterest_access_token, create_pinterest_pin
from django.http import HttpResponse, HttpResponseBadRequest
from .models import PinUser
from site_scan.models import BlogPost
import logging
import re

logger = logging.getLogger(__name__)


def home(request):
    if request.user.is_staff:
        context = {}
        return render(request, "social_publish/publish.html", context)
    else:
        return render(request, "home.html")


def pin_publish(request):
    pin_data = {}

    # Log the entire request.POST to see what data is coming in
    logger.info("Request POST data: %s", request.POST)

    for k, v in request.POST.lists():  # Use lists() to handle multiple values
        logger.info("Processing key: %s, value: %s", k, v)  # Add logging here
        match = re.match(r'(\w+)_(\d+)(\[\])?$', k)
        if match:
            field, post_id, is_list = match.groups()

            if post_id not in pin_data:
                pin_data[post_id] = {}
            try:
                blogpost = BlogPost.objects.get(id=post_id)
                pin_data[post_id]['link'] = blogpost.url
                if blogpost.pin_image_url:
                    pin_data[post_id]['pin_image_url'] = blogpost.pin_image_url
            except BlogPost.DoesNotExist:
                raise Exception(f"BlogPost with ID {post_id} not found")

            if field == 'title':
                pin_data[post_id]['title'] = v[0]  # v is a list, take the first element
            elif field == 'description':
                pin_data[post_id]['description'] = v[0]  # v is a list, take the first element
            elif field == 'boards' and is_list:
                pin_data[post_id]['boards'] = v  # v is already a list
            elif field == 'image':
                pin_data[post_id]['image'] = v[0]  # v is a list, take the first element

    logger.info("Pin data after processing: %s", pin_data)

    total_pins_created = 0

    for post_id, pin in pin_data.items():
        logger.info(f"Saving pin for post {post_id}: {pin}")
        pin_user = PinUser.objects.get(user=request.user)
        boards = pin.get('boards', [])
        for board_id in boards:
            pin_copy = pin.copy()  # Create a copy to modify for each board
            pin_copy['board'] = board_id
            create_pinterest_pin(post_id, pin_copy, pin_user)
            pin_image_url = pin_copy.get('pin_image_url', None)
            if pin_image_url is not None:
                pin_copy['image'] = pin_image_url
                create_pinterest_pin(post_id, pin_copy, pin_user)
            total_pins_created += 1  # Increment total_pins_created for each pin created

    context = {
        'success_message': f"{total_pins_created} pins published successfully!"
    }
    return render(request, 'home.html', context)


def new_board(request):
    pass


def save_pinterest_access_token(request, access_token, refresh_token, access_token_expiration,
                                refresh_token_expiration):
    # Ensure the user is logged in
    if request.user.is_authenticated:
        # Get or create the associated PinUser object
        pin_user, created = PinUser.objects.get_or_create(user=request.user)

        # Update the access_token field
        pin_user.access_token = access_token
        pin_user.refresh_token = refresh_token
        pin_user.access_token_expiration_dt = access_token_expiration
        pin_user.refresh_token_expiration_dt = refresh_token_expiration
        pin_user.save()


def pinterest_access_token(request):
    # Print GET parameters
    for key, value in request.GET.items():
        print(f"GET parameter: {key} = {value}")

    # Print POST parameters
    for key, value in request.POST.items():
        print(f"POST parameter: {key} = {value}")

    # Alternatively, you can print all parameters (GET and POST) together
    for key, value in request.GET.items():
        print(f"All parameter: {key} = {value}")
    for key, value in request.POST.items():
        print(f"All parameter: {key} = {value}")

    # If you want to print all the request headers:
    for key, value in request.META.items():
        if key.startswith('HTTP_'):
            print(f"Header: {key[5:]} = {value}")

    context = {
        'success_message': "Your Pinterest account has been connected!"
    }
    return render(request, 'home.html', context)


# Receive the access code with your redirect URI
def pinterest_auth(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code or not state:
        logger.error('Pinterest OAuth failed: Missing code or state parameter')
        return HttpResponseBadRequest('Pinterest OAuth failed: Missing code or state parameter')

    if state != 'rtw-pinner':
        logger.error('Pinterest OAuth failed: Invalid state parameter')
        return HttpResponseBadRequest('Pinterest OAuth failed: Invalid state parameter')

    # Perform API requests using the received code to exchange for access token
    # Handle storing the access token and user data as needed
    logger.info(f"User authorized Pinterest access. Code: {code}, State: {state}")

    access_token, refresh_token, access_token_expiration, refresh_token_expiration = get_pinterest_access_token(code,
                                                                                                                state)

    if access_token and refresh_token:
        # Access token and refresh token are valid, you can use them as needed.
        logger.info(f'Access Token: {access_token}')
        logger.info(f'Refresh Token: {refresh_token}')
        # Save data
        save_pinterest_access_token(request, access_token, refresh_token, access_token_expiration,
                                    refresh_token_expiration)
        context = {
            'success_message': "Your Pinterest account has been connected!"
        }
        return render(request, 'home.html', context)
    else:
        context = {
            'error_message': "We experienced an error connecting to your Pinterest account. Please contact us for support."
        }
        return render(request, 'home.html', context)
