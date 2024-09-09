from django.core.management.base import BaseCommand, CommandError
from trends.models import BatchRequest, BatchResult, Keyword
from django.db.models.functions import Length
from .client import RestClient
from environs import Env
import re
from django.db.models import Q


class Command(BaseCommand):
    help = 'Seeds database with Keyword Difficulty scores.'

    def handle(self, *args, **options):
        prepare_kw_list()


def prepare_kw_list():
    # either the volume is null or empty, or the difficulty is null or empty.
    all_records = Keyword.objects.filter(Q(volume__isnull=True) | Q(difficulty__isnull=True))
    print(len(all_records), 'keywords need updated SEO data')
    # DataforSEO only accepts 1k rows max per call
    if len(all_records) > 999:
        print('1k records, need to split')
        split_kw_list(all_records)
    else:
        fetch_data(all_records)


# Only 1k keywords may be requested from the API per call
def split_kw_list(all_records):
    length = len(all_records)
    print('Total records', length)
    thousand_chunks = length // 1000
    remainder = length % 1000
    # Fetch the keyword difficulties in a thousand kw chunks.
    all_lists = []
    for i in range(0, thousand_chunks):
        print("Fetching records ", i * 1000, "-", 999 + (i * 1000))
        # added one because python stop is not inclusive
        all_lists.append(all_records[(i * 1000):(999 + (i * 1000) + 1)])
    # Fetch the remaining keyword difficulties
    # remainder - 1 because we are fetching indices and the last record will be len-1
    print("Fetching records ", thousand_chunks * 1000, "-", (thousand_chunks * 1000) + (remainder - 1))
    all_lists.append(all_records[(thousand_chunks * 1000):((thousand_chunks * 1000) + (remainder - 1) + 1)])

    # build lists of 1k max keywords for DataforSEO API calls
    for lst in all_lists:
        fetch_data(lst)


# req_type is either difficulty or volume
def fetch_data(kw_list):
    new_list = []
    for x in kw_list:
        # remove any symbols that are not a dash, space or letter
        sanitized_string = re.sub(r"[^a-zA-Z\- ]+", "", x.keyword)
        # The maximum number of characters for each keyword: 80
        # The maximum number of words for each keyword phrase: 10
        if 8 < len(sanitized_string) <= 80 and sanitized_string.count(' ') <= 9:
            new_list.append(sanitized_string)
    fetch_volume(new_list)
    fetch_difficulty(new_list)


def fetch_difficulty(keywords):
    env = Env()
    env.read_env()  # read .env file, if it exists
    user = env("LOGIN")  # => 'sloria'
    secret = env("PASSWORD")  # => raises error if not se
    # You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
    # client = RestClient(env("LOGIN"), env("PASSWORD"))
    client = RestClient(user, secret)
    post_data = dict()
    # simple way to set a task
    post_data[len(post_data)] = dict(
        keywords=keywords,
        location_name="United States",
        language_name="English"
    )
    # POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
    print('Fetching difficulty scores')
    response = client.post("/v3/dataforseo_labs/google/bulk_keyword_difficulty/live", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        print(response)
        process_results(response, 'difficulty')
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


def fetch_volume(keywords):
    env = Env()
    env.read_env()  # read .env file, if it exists
    user = env("LOGIN")  # => 'sloria'
    secret = env("PASSWORD")  # => raises error if not se
    # You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
    # client = RestClient(env("LOGIN"), env("PASSWORD"))
    client = RestClient(user, secret)
    post_data = dict()
    # simple way to set a task
    post_data[len(post_data)] = dict(
        keywords=keywords,
        location_name="United States",
        language_name="English"
    )
    # POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
    response = client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        print(response)
        process_results(response, 'volume')
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


def process_results(response, data_type):
    if data_type == 'volume':
        results = response['tasks'][0]['result']
        for item in results:
            print(item["keyword"], item["search_volume"])
            Keyword.objects.filter(keyword=item["keyword"]).update(volume=item["search_volume"])
    elif data_type == 'difficulty':
        results = response['tasks'][0]['result'][0]['items']
        for item in results:
            Keyword.objects.filter(keyword=item["keyword"]).update(difficulty=item["keyword_difficulty"])
