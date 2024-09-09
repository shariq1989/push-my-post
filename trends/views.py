from django.db.models import Count, Sum, Q, F
from django.shortcuts import render, redirect
from .client import RestClient
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from environs import Env
from pytz import timezone
import time
import json
import logging

from .service import sanitize_list, sanitize_kw, fetch_seo_data, process_seo_results, setup_client, \
    get_this_quarter_and_month, search_data_for_month, filter_search_res_by_kw
from trends.models import BatchResult, Trending, RelatedKeyword, Keyword, TrendingBatch

logger = logging.getLogger(__name__)


def route_to_previous_page(request):
    previous_page = request.POST.get('previous_page', None)
    if previous_page:
        return redirect(previous_page)
    else:
        return render(request, "trends/search_results.html", {})


def search(request):
    phrase = request.POST.get("search_input")
    if not phrase:
        return route_to_previous_page(request)
    search_res = BatchResult.objects.filter(keyword__keyword__icontains=phrase).values(
        'result_id', 'batch_id', 'keyword__keyword', 'frequency', 'batch__timeframe_string', 'batch__keyword',
        'batch__begin_date', 'batch__end_date').order_by('-frequency')
    if not search_res:
        return route_to_previous_page(request)
    search_res_months = []
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    # distribute results across the 12 months
    for x in range(12):
        search_res_months.append([search_res.filter(batch__begin_date__month=x + 1).values('keyword__keyword').annotate(
            count=Count('keyword__keyword')).annotate(
            total=Sum('frequency')).order_by(
            '-count', '-total').filter(
            count__gt=1), months[x]])
    context = {
        'search_res': search_res_months
    }
    return render(request, "trends/search_results.html", context)


def result_details(request, seed_keyword):
    print('Requesting related queries for ', seed_keyword)
    rising_res = RelatedKeyword.objects.filter(keyword__keyword=seed_keyword, type='rising') \
        .values('keyword__keyword', 'related_keyword__difficulty', 'related_keyword__keyword', 'frequency',
                'type').order_by(
        '-frequency')
    top_res = RelatedKeyword.objects.filter(keyword__keyword=seed_keyword, type='top') \
        .values('keyword__keyword', 'related_keyword__difficulty', 'related_keyword__keyword', 'frequency',
                'type').order_by(
        '-frequency')
    interest = Keyword.objects.filter(keyword=seed_keyword) \
        .values('interest')
    if rising_res and top_res and interest[0]['interest']:
        # just display results from the db
        print("Found trends for the day in db, just using them")
        interest = interest[0]
        interest = json.loads(interest['interest'])
        pass
    else:
        kw_list = []
        keyword_data = fetch_kw_detail(seed_keyword)
        rising = keyword_data['rising']
        top = keyword_data['top']
        interest = keyword_data['interest']
        if rising is not None:
            seed_kw_id, created_bool = Keyword.objects.get_or_create(keyword=seed_keyword)
            for rising_stats in rising:
                rising_keyword = rising_stats['query']
                rising_val = rising_stats['value']
                sanitized_kw = sanitize_kw(rising_keyword)
                if sanitized_kw:
                    kw_list.append(rising_keyword)
                    kw_id, created_bool = Keyword.objects.get_or_create(keyword=rising_keyword)
                    row = RelatedKeyword(keyword=seed_kw_id, related_keyword=kw_id, frequency=rising_val,
                                         type='rising')
                    row.save()
            rising_res = RelatedKeyword.objects.filter(keyword=seed_kw_id, type='rising') \
                .values('keyword__keyword', 'related_keyword__difficulty', 'related_keyword__keyword', 'frequency',
                        'type').order_by('-frequency')
        if top is not None:
            seed_kw_id, created_bool = Keyword.objects.get_or_create(keyword=seed_keyword)
            for top_stats in top:
                top_keyword = top_stats['query']
                top_val = top_stats['value']
                sanitized_kw = sanitize_kw(top_keyword)
                if sanitized_kw:
                    kw_list.append(top_keyword)
                    kw_id, created_bool = Keyword.objects.get_or_create(keyword=top_keyword)
                    row = RelatedKeyword(keyword=seed_kw_id, related_keyword=kw_id, frequency=top_val,
                                         type='top')
                    row.save()
            top_res = RelatedKeyword.objects.filter(keyword__keyword=seed_keyword, type='top') \
                .values('keyword__keyword', 'related_keyword__difficulty', 'related_keyword__keyword', 'frequency',
                        'type').order_by('-frequency')
        if interest is not None:
            interest_dump = json.dumps(interest)
            Keyword.objects.filter(keyword=seed_keyword).update(interest=interest_dump)
        fetch_seo_data(kw_list)

    # trend score
    interest_y = []
    interest_x = []
    if interest is not None:
        for segment in interest:
            if not segment['missing_data']:
                interest_y.append(segment['date_to'])
                interest_x.append(segment['values'][0])

    context = {
        'keyword': seed_keyword,
        'rising_res': rising_res,
        'top_res': top_res,
        'labels': interest_y,
        'data': interest_x
    }
    return render(request, "trends/results_details.html", context)


def add_weeks(num_weeks, custom_date=None):
    today = datetime.now()
    if custom_date:
        today = custom_date
    future = today + timedelta(weeks=+num_weeks)
    return future.isocalendar()[1]


def add_months(num_months):
    today = datetime.now()
    future = today + relativedelta(months=+num_months)
    return future.month


def run_q_filter(filter_phrase):
    search_res = BatchResult.objects.filter(filter_phrase).values(
        'result_id', 'batch_id', 'keyword__keyword', 'frequency', 'batch__timeframe_string', 'batch__keyword',
        'batch__begin_date', 'batch__end_date')
    # print(search_res)
    recipe_rs, how_cook_rs = filter_search_res_by_kw(search_res)
    return recipe_rs, how_cook_rs


def quarterly_plan(request):
    context = {
        "trends_data":
            {"This month": ["two_weeks", run_q_filter(
                Q(batch__begin_date__month=add_months(0), batch__begin_date__day__lte=25))],
             "Next Month": ["three_weeks", run_q_filter(
                 Q(batch__begin_date__month=add_months(1), batch__begin_date__day__lte=25))],
             "2 Months": ["four_weeks", run_q_filter(
                 Q(batch__begin_date__month=add_months(2), batch__begin_date__day__lte=25))]
             }
    }
    # print(context)
    return render(request, "trends/multi_trends.html", context)


def display_quarter(request, quarter=-1, month=0):
    if quarter == -1:
        # print("month is zero")
        quarter, month = get_this_quarter_and_month()
    # print("month", month, "quarter", quarter)
    quarter = int(quarter)
    if quarter == 1:
        months_list = [["January", "01"], ["February", "02"], ["March", "03"]]
    elif quarter == 2:
        months_list = [["April", "04"], ["May", "05"], ["June", "06"]]
    elif quarter == 3:
        months_list = [["July", "07"], ["August", "08"], ["September", "09"]]
    else:
        months_list = [["October", "10"], ["November", "11"], ["December", "12"]]

    context = {
        "months_list": months_list,
        "quarter_num": quarter
    }
    if month == 0:
        month = months_list[0][1]
    month_data = search_data_for_month(request, str(month))
    context.update(month_data)
    return render(request, "trends/multi_trends.html", context)


def trending(request):
    latest_batch = TrendingBatch.objects.filter(completed=True).latest('created_on')
    recipe_res = Trending.objects.filter(type='recipe', batch=latest_batch).values('keyword__keyword',
                                                                                   'keyword__difficulty',
                                                                                   'keyword__volume',
                                                                                   'frequency').order_by(
        '-frequency')
    how_res = Trending.objects.filter(type='how cook', batch=latest_batch).values('keyword__keyword',
                                                                                  'keyword__difficulty',
                                                                                  'keyword__volume',
                                                                                  'frequency').order_by(
        '-frequency')
    context = {
        'batch': latest_batch,
        'recipe_res': recipe_res,
        'how_res': how_res
    }
    return render(request, "trends/trending_res.html", context)


def fetch_kw_detail(seed_keyword):
    client = setup_client()
    post_data = dict()
    # simple way to set a task
    post_data[len(post_data)] = dict(
        time_range='past_5_years',
        keywords=[seed_keyword],
        type='web'
    )
    print(f"Fetching kw detail {post_data}")
    url = "/v3/keywords_data/google_trends/explore/live"
    response = client.post(url, post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        return process_kw_details_results(response)
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))


def process_kw_details_results(response):
    top, rising, interest = None, None, None
    items = response['tasks'][0]['result'][0]['items']
    for item in items:
        if item['type'] == 'google_trends_graph':
            interest = item['data']
        elif item['type'] == 'google_trends_queries_list':
            rising = item['data']['rising']
            top = item['data']['top']
    return {'top': top, 'rising': rising, 'interest': interest}
