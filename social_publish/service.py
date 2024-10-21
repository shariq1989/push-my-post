import logging
import requests
import base64
import time
from typing import Dict, Any, Optional
from celery import shared_task
from requests.exceptions import HTTPError
from django.utils import timezone
from environs import Env
from django.db import transaction
from .models import PinBoard, PinUser, PinterestPin
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)

env = Env()
env.read_env()  # read .env file, if it exists

PINTEREST_APP_ID = env("PINTEREST_APP_ID")
PINTEREST_SECRET_KEY = env("PINTEREST_SECRET_KEY")
TWITTER_API_KEY = env("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = env("TWITTER_API_KEY_SECRET")
TWITTER_BEARER_TOKEN = env("TWITTER_BEARER_TOKEN")
TWITTER_ACCESS_TOKEN = env("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = env("TWITTER_ACCESS_TOKEN_SECRET")

# Global variables for rate limiting
rate_limits = {
    "org_write": {"calls_per_min": 90, "reset_time": time.time() + 60},
    "org_read": {"calls_per_min": 900, "reset_time": time.time() + 60},
    # Add other categories as needed
}


# Receive the access code with your redirect URI
# https://developers.pinterest.com/docs/getting-started/authentication/#2.%20Receive%20the%20access%20code%20with%20your%20redirect%20URI
def pinterest_login():
    client_id = PINTEREST_APP_ID
    redirect_uri = 'https://pushmypost.com/social_publish/pinterest-auth'
    scope = 'boards:read,boards:write,pins:read,pins:write'
    state = 'rtw-pinner'
    pinterest_oauth_url = f'https://www.pinterest.com/oauth/?' \
                          f'client_id={client_id}&' \
                          f'redirect_uri={redirect_uri}&' \
                          f'response_type=code&scope={scope}&' \
                          f'state={state}'
    print(f"Making Pinterest OAuth Request: {pinterest_oauth_url}")
    return HttpResponseRedirect(pinterest_oauth_url)


# Exchange the code for an access token
# https://developers.pinterest.com/docs/getting-started/authentication/#3.%20Exchange%20the%20code%20for%20an%20access%20token
def get_pinterest_access_token(code, state):
    # Define the endpoint URL
    token_url = 'https://api.pinterest.com/v5/oauth/token'
    redirect_uri = 'https://pushmypost.com/social_publish/pinterest-access_token'
    # Prepare the authorization header using client_id and client_secret
    auth_header = f'{PINTEREST_APP_ID}:{PINTEREST_SECRET_KEY}'
    encoded_auth_header = base64.b64encode(auth_header.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Prepare the request data
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }

    # Make the POST request
    response = requests.post(token_url, headers=headers, data=data)
    print(f"Exchanging auth code for access token: token: {token_url}, headers:{headers}, data:{data}")
    print(f"Response from Pinterest Access Token req: {response}")
    print(f"Response from Pinterest Access Token req: {response.text}")

    # Check for a successful response
    if response.status_code == 200:
        access_token_response = response.json()
        access_token = access_token_response.get('access_token')
        refresh_token = access_token_response.get('refresh_token')
        access_token_expiration = timezone.now() + timezone.timedelta(
            seconds=access_token_response.get('expires_in'))
        refresh_token_expiration = timezone.now() + timezone.timedelta(
            seconds=access_token_response.get('refresh_token_expires_in'))

        return access_token, refresh_token, access_token_expiration, refresh_token_expiration
    else:
        # Handle the case where the request fails
        error_message = response.text
        print(f'Pinterest OAuth request failed with status code {response.status_code}')
        print(f'Error message: {error_message}')
        return None, None


def create_tweet(tweet_data):
    url = 'https://api.twitter.com/2/tweets'
    headers = {
        'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=tweet_data)
    access_level = response.headers.get('x-access-level')
    logger.info(f"Twitter API access level: {access_level}")
    print(f"Twitter API access level: {access_level}")

    # Handle rate limiting
    if response.status_code == 429:
        reset_time = 60
        if reset_time:
            sleep_time = int(reset_time) - int(time.time())
            if sleep_time > 0:
                print(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                return create_tweet(tweet_data)

    response.raise_for_status()
    return response.json()


def reset_rate_limits():
    """Function to reset rate limits after hitting them."""
    for category in rate_limits:
        if category == 'org_write':
            rate_limits[category]["remaining"] = 100
            rate_limits[category]["reset_time"] = time.time() + 60
        elif category == 'org_read':
            rate_limits[category]["remaining"] = 900
            rate_limits[category]["reset_time"] = time.time() + 60


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def request_pinterest(
        self,
        endpoint: str,
        category: str = 'org_write',
        call_type: str = 'get',
        data: Optional[Dict[str, Any]] = None,
        access_token: Optional[str] = None,
        query_params: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    global rate_limits

    if not isinstance(category, str):
        raise TypeError(f"'category' must be a string, not {type(category)}")

    if category not in rate_limits:
        raise ValueError(f"Unknown category: {category}. Valid categories are: {', '.join(rate_limits.keys())}")

    if access_token is None:
        logger.error("No Pinterest access token passed.")
        print(f'Pinterest request. Endpoint: {endpoint}, call: {call_type}, data: {data}')
        return None

    url = f'https://api.pinterest.com/v5/{endpoint}'
    if query_params:
        url += query_params

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    reset_rate_limits()  # Reset rate limits if necessary

    if rate_limits[category]["remaining"] <= 1:
        wait_time = 60 - (time.time() - rate_limits[category]["reset_time"])
        print(f"Rate limit reached for {category}. Waiting for {wait_time:.2f} seconds.")
        time.sleep(max(wait_time, 0))
        reset_rate_limits()  # Reset again after waiting

    rate_limits[category]["remaining"] -= 1  # Decrement remaining calls

    try:
        if call_type == 'get':
            response = requests.get(url, headers=headers)
        elif call_type == 'post':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported call_type: {call_type}. Use 'get' or 'post'.")

        response.raise_for_status()

        resp_json = response.json()
        if response.status_code not in {200, 201}:
            error_message = resp_json
            logger.error(f"Pinterest API error ({response.status_code}): {error_message}")
            raise Exception(
                f"Error making Pinterest API request. Endpoint: {endpoint}, call: {call_type}, headers: {headers}, data: {data}")

    except requests.exceptions.RequestException as e:
        if response.status_code == 429:
            print(f"Rate limit exceeded for {category}. Retrying after 60 seconds.")
            self.retry(exc=e)  # Celery will automatically retry after delay
        else:
            logger.error(f"Error making Pinterest call: {e}")
            print(f'Pinterest request. Endpoint: {endpoint}, call: {call_type}, headers:{headers} data: {data}')
            raise Exception("Error fetching data from Pinterest") from e

    print(f'Pinterest Response: {resp_json}')
    return resp_json


def create_board(name, description, privacy='PUBLIC'):
    data = {
        "name": name,
        "description": description,
        "privacy": privacy
    }
    resp = request_pinterest('boards', 'post', data)
    save_board(resp)
    return resp


def save_board(resp):
    new_board = PinBoard(board_id=resp['id'],
                         name=resp['name'], description=resp['description'], pin_count=resp['pin_count'],
                         follower_count=resp['follower_count'])
    new_board.save()


def delete_board(name):
    data = {
        "name": name
    }
    resp = request_pinterest('boards', 'post', data)
    return resp


# Input Args
#   post_id : 24
#   input_data: {'title': 'Pumpkin Protein Balls',
#   'description': 'Healthy no-bake pumpkin....\r\n',                                ',
#   'board': '333970197307132906'}
def create_pinterest_pin(post_id, input_data, pin_user):
    # Pinterest API endpoint for creating a pin
    api_endpoint = 'pins'

    # Data for creating the pin
    pin_data = {
        "title": input_data['title'],
        "description": input_data['description'],
        "board_id": input_data['board'],
        "link": input_data['link'],
        # TODO: "dominant_color":,
        # TODO: alt text,
        "media_source": {
            "source_type": "image_url",
            "url": input_data['image']
        }
    }

    try:
        # Call the Celery task to request Pinterest asynchronously
        task = request_pinterest.delay(
            endpoint=api_endpoint,
            category='org_write',  # Or another category based on your rate limits
            call_type='post',
            data=pin_data,
            access_token=pin_user.access_token
        )

        # Optionally check task status (non-blocking) or handle post-task logic here
        logger.info(f"Pin creation task queued for post_id {post_id}. Task ID: {task.id}")
        return task.id

    except Exception as e:
        # Handle exceptions that may occur when queuing the task
        logger.error(f"Failed to queue Pinterest pin creation task for post_id {post_id}: {e}")
        return None


def get_boards(pin_user):
    resp = request_pinterest('boards', category='org_read', access_token=pin_user.access_token)
    pin_boards = []
    if resp['items'] is not None:
        pin_boards.extend(resp['items'])
    bookmark = resp['bookmark']
    while bookmark is not None:
        query_param = '?bookmark=' + resp['bookmark']
        resp = request_pinterest('boards', category='org_read', access_token=pin_user.access_token,
                                 query_params=query_param)
        pin_boards.extend(resp['items'])
        bookmark = resp['bookmark']
    return pin_boards


def get_pinterest_user_data(pin_user):
    boards = get_boards(pin_user)
    # logger.info(f"Boards from pinterest {boards}")
    return boards
