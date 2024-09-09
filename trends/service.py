import re
import logging
import calendar
from environs import Env
from datetime import date, datetime, timedelta
from pytz import timezone
from django.db.models import Count, Sum, Q, F
from django.db import transaction
from .client import RestClient
from trends.models import Keyword, TrendingBatch, Trending, BatchResult

logger = logging.getLogger(__name__)


def filter_search_res_by_kw(search_res):
    # print(search_res)
    recipe_rs = search_res.filter(batch__keyword='recipe').values('keyword__keyword', 'keyword__difficulty',
                                                                  'keyword__volume') \
        .annotate(count=Count('keyword__keyword')) \
        .annotate(score=Sum('frequency')) \
        .order_by('-count', '-score').filter(count__gt=1)
    # print('Recipe Only')
    # print(recipe_rs)

    how_cook_rs = search_res.filter(batch__keyword='how cook').values('keyword__keyword',
                                                                      'keyword__difficulty', 'keyword__volume') \
        .annotate(count=Count('keyword__keyword')) \
        .annotate(score=Sum('frequency')) \
        .order_by('-count', '-score').filter(count__gt=1)
    # print('How To Cook')
    # print(how_cook_rs)
    return recipe_rs, how_cook_rs


def search_data_for_month(request, month):
    search_res = BatchResult.objects.filter(batch__begin_date__month=month, batch__begin_date__day__lte=25).values(
        'result_id', 'batch_id', 'keyword__keyword', 'keyword__difficulty', 'keyword__volume', 'frequency',
        'batch__timeframe_string', 'batch__keyword', 'batch__begin_date', 'batch__end_date')
    # print(search_res)
    text_month = calendar.month_name[int(month)]
    recipe_rs, how_cook_rs = filter_search_res_by_kw(search_res)
    context = {
        'how_res': how_cook_rs,
        'recipe_res': recipe_rs,
        'text_month': text_month,
        'month': month
    }
    return context


def get_this_quarter_and_month():
    today = datetime.now()
    month = today.month
    quarter = ((month - 1) // 3) + 1
    if month < 10:
        month = "0" + str(month)
    else:
        month = str(month)
    return quarter, month


def sanitize_list(kw_list):
    # print(f"Original kw list {kw_list}")
    if len(kw_list) == 0:
        logger.warning('Sanitize kw service called with empty kw list')
        return []
    sanitized = []
    for kw in kw_list:
        # don't call on nulls
        if kw:
            sanitized_kw = sanitize_kw(kw)
            # dont call on nulls
            if sanitized_kw:
                sanitized.append(sanitized_kw)
    return sanitized


def sanitize_kw(keyword):
    # remove any symbols that are not a dash, space or letter
    sanitized_string = re.sub(r"[^a-zA-Z\- ]+", "", keyword)
    # The maximum number of characters for each keyword: 80
    # The maximum number of words for each keyword phrase: 10
    if 8 < len(sanitized_string) <= 80 and sanitized_string.count(' ') <= 9:
        return sanitized_string
    else:
        logger.warning(f"Ignoring {keyword=} failed sanitizing.")


# given keywords, this method fetches keyword difficulty for each one
def fetch_seo_data(kw_list):
    client = setup_client()
    post_data = dict()
    print(f'Sanitizing a list of {len(kw_list)} keywords')
    sanitized = sanitize_list(kw_list)
    if len(sanitized) > 0:
        print(f'Requesting difficulty for {len(sanitized)} keywords')
        post_data[len(post_data)] = dict(
            keywords=sanitized,
            location_name="United States",
            language_name="English"
        )
        # POST /v3/dataforseo_labs/google/bulk_keyword_difficulty/live
        response = client.post("/v3/dataforseo_labs/google/bulk_keyword_difficulty/live", post_data)
        # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
        if response["status_code"] == 20000:
            # print("Response from DataforSEO")
            # print(response)
            process_seo_results(response, post_data)
        else:
            logger.error("Error occurred fetching bulk kw difficulty")
            print(f"Code:{response['status_code']} Message: {response['status_message']}")
            print(f"Request was {post_data}")
    else:
        print(f"Sanitized list had 0 keywords, not requesting difficulty. {kw_list=}")


def process_seo_results(response, post_data):
    task = response['tasks'][0]
    if task['status_code'] == 20000:
        results = task['result'][0]['items']
        for item in results:
            Keyword.objects.filter(keyword=item["keyword"]).update(difficulty=item["keyword_difficulty"])
    else:
        logger.error("Error occurred processing bulk difficulty results")
        print(f"Response: Code:{response['status_code']} Message: {response['status_message']}")
        print(f"Task: Code:{task['status_code']} Message: {task['status_message']}")
        print(f"Request was {post_data}")


def setup_client():
    env = Env()
    env.read_env()  # read .env file, if it exists
    user = env("LOGIN")  # => 'sloria'
    secret = env("PASSWORD")  # => raises error if not se
    # You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
    client = RestClient(user, secret)
    return client


def trends_standard_post(begin_date, end_date, keyword=None):
    client = setup_client()
    post_data = dict()
    if keyword is None:
        keyword = ['how cook', 'recipe']
    else:
        keyword = [keyword]
    post_data[len(post_data)] = dict(
        date_from=begin_date,
        date_to=end_date,
        keywords=keyword,
        type='web'
    )
    response = client.post("/v3/keywords_data/google_trends/explore/task_post", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        return response
    else:
        return [False, "D4S Error: Code: " + response["status_code"] + ", Message: " + response["status_message"]]


def store_trends_post(db_resp):
    res_id = db_resp['tasks'][0]['id']
    new_batch = TrendingBatch(d4s_id=res_id)
    new_batch.save()


def fetch_trending_keywords(begin_date, end_date, keyword=None):
    client = setup_client()
    post_data = dict()
    if keyword is None:
        keyword = ['how cook', 'recipe']
    else:
        keyword = [keyword]
    post_data[len(post_data)] = dict(
        date_from=begin_date,
        date_to=end_date,
        keywords=keyword,
        type='web',

    )
    url = "/v3/keywords_data/google_trends/explore/live"
    response = client.post(url, post_data)
    if response["status_code"] == 20000:
        test_res = trends_standard_get_checks(response)
        # Test returned True
        if test_res[0]:
            resp = store_trends_get(response)
            return [True, resp]
        else:
            # Some test failed
            logger.error(test_res)
            return test_res
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


def calling_live_trends():
    tz = timezone('EST')
    end_date = datetime.now(tz)
    begin_date = end_date - timedelta(5)
    trending_results = fetch_trending_keywords(begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))


def process_trends_results_live(response, keyword):
    results = response['tasks'][0]['result'][0]['items']
    return_dict = {}
    for seed_keyword in keyword:
        for res in results:
            if res['type'] == 'google_trends_queries_list' and res['keywords'][0] == seed_keyword:
                return_dict[seed_keyword] = res['data']['rising']
    return return_dict


def trends_standard_get():
    client = setup_client()
    latest_batch = TrendingBatch.objects.filter(completed=False).latest('created_on')
    print(latest_batch)
    if latest_batch:
        get_string = "/v3/keywords_data/google_trends/explore/task_get/" + latest_batch.d4s_id
        response = client.get(get_string)
        # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
        if response["status_code"] == 20000:
            test_res = trends_standard_get_checks(response)
            # Test returned True
            if test_res[0]:
                resp = store_trends_get(response)
                return [True, resp]
            else:
                # Some test failed
                logger.error(test_res)
                return test_res
        else:
            return [False, "D4S Error: Code: " + response["status_code"] + ", Message: " + response["status_message"]]
    else:
        message = "Error fetching latest_batch in trends_standard_get"
        logger.error(message)
        return [False, message]


def trends_standard_get_checks(response):
    if not response['tasks']:
        return [False, 'D4S Error: No tasks object in response']
    if not response['tasks'][0]:
        return [False, 'D4S Error: Could not access 0th object in tasks']
    task = response['tasks'][0]
    if not task['result']:
        return [False, 'D4S Error: No result object in task']
    if not task['result'][0]:
        return [False, 'D4S Error: Could not access 0th result']
    result = task['result'][0]
    if not result['check_url']:
        return [False, 'D4S Error: Could not access Google trends URL']
    items = result['items']
    recipe_found = False
    for item in items:
        if item['type'] == 'google_trends_queries_list':
            if item['keywords'][0] == 'recipe':
                recipe_found = True
    if not recipe_found:
        return [False, 'D4S Error: Recipe keywords not returned']
    return [True, response]


def process_trends_results(response):
    task = response['tasks'][0]
    return_dict = {'id': task['id']}
    result = task['result'][0]
    return_dict['trends_url'] = result['check_url']
    items = result['items']
    for item in items:
        if item['type'] == 'google_trends_queries_list':
            return_dict[item['keywords'][0]] = item['data']['rising']
    return return_dict


def store_trends_get(response, keywords=None):
    parsed_resp = process_trends_results(response)
    if keywords is None:
        keywords = ['how cook', 'recipe']
    kw_list = []
    # Wrap the code within a transaction
    with transaction.atomic():
        trending_batch = TrendingBatch.objects.get(d4s_id=parsed_resp['id'])
        trending_objs = []
        for seed_kw in keywords:
            if seed_kw in parsed_resp:
                for kw in parsed_resp[seed_kw]:
                    sanitized_kw = sanitize_kw(kw['query'])
                    if sanitized_kw:
                        kw_list.append(kw['query'])
                        keyword_obj, _ = Keyword.objects.get_or_create(keyword=kw['query'])
                        trending_obj = Trending(keyword=keyword_obj, frequency=kw['value'], type=seed_kw,
                                                batch=trending_batch)
                        trending_objs.append(trending_obj)
        # Bulk create the Trending objects with assigned keywords in a single database query
        Trending.objects.bulk_create(trending_objs)

    trending_batch.google_trends_url = parsed_resp['trends_url']
    trending_batch.completed = True
    trending_batch.save()
    if kw_list:
        fetch_seo_data(kw_list)
    else:
        logger.error("No Trending Keywords found for last 5 days")
    return parsed_resp
