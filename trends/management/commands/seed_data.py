from django.core.management.base import BaseCommand, CommandError
from trends.models import BatchRequest, BatchResult, Keyword
import time
import psycopg2

from datetime import date, datetime, timedelta
from pytrends.request import TrendReq

from trends.models import BatchRequest, BatchResult


class Command(BaseCommand):
    help = 'Seeds database with Google Trends data'

    def handle(self, *args, **options):
        # start searching trends from this date
        begin_date = date(2016, 1, 1)
        while begin_date < (date(2022, 10, 1) - timedelta(14)):
            # find end date for trend search
            end_date = return_next_increment(begin_date)
            timeframe = begin_date.strftime("%Y-%m-%d") + ' ' + end_date.strftime("%Y-%m-%d")
            fetch_kw(timeframe, begin_date, end_date)
            self.stdout.write(self.style.SUCCESS('Fetched data for "%s"' % timeframe))
            # fetch complete, move begin_date to next period.
            # Add a day because the next period should not overlap
            begin_date = end_date + timedelta(days=1)


# promote date
# 01-01-2000 -> 01-15-2000
# 01-15-2000 -> END OF JANUARY
def return_next_increment(start_date):
    # beginning of month
    if start_date.day == 1:
        # return mid-month
        return start_date + timedelta(days=14)
    # mid-month
    elif 13 < start_date.day < 17:
        # return end of month
        # go to beginning of next month
        if start_date.month == 12:
            new_date = date(start_date.year + 1, 1, 1)
        else:
            new_date = date(start_date.year, start_date.month + 1, 1)
        # go back one day for end of month
        return new_date - timedelta(days=1)
    # end of month
    else:
        return start_date + timedelta(days=1)


def fetch_kw(search_timeframe, start_date, end_date):
    pytrend = TrendReq()
    # Get Google Keyword Suggestions
    # keywords how to cook, healthy, recipe, keto recipe, instant pot recipe, air fryer recipe
    kw_list = ['recipe', 'how cook']
    # TODO: gprop="youtube"
    for keyword in kw_list:
        # 5 years, 3 months, week, 4 hours
        # timeframes = [
        # 'today 5-y', 'today 3-m', 'now 7-d', 'now 1-d',
        # 'now 4-H',
        # ]
        pytrend.build_payload(kw_list=[keyword], timeframe=search_timeframe)
        fetch_data(pytrend, keyword, search_timeframe, start_date, end_date)
        # debugging : for stopping after one run
        # exit()
    time.sleep(30)


def fetch_data(pytrend, keyword, search_timeframe, start_date, end_date):
    # get data for kw
    print('Requesting data for keyword:', keyword, ', timeframe: ', search_timeframe)
    related_queries = pytrend.related_queries()
    # Ignoring top results
    # top = related_queries[keyword]["top"]
    rising = related_queries[keyword]["rising"]
    # TODO add related topics
    # related_topic = pytrend.related_topics()
    # print("related")
    # print(related_topic[keyword]["rising"])
    # TODO: insert batch results
    insert_results(keyword, search_timeframe, start_date, end_date, rising.to_dict())


def insert_results(keyword, search_timeframe, start_date, end_date, rising):
    # create batch record
    new_batch = BatchRequest(timeframe_string=search_timeframe, keyword=keyword, begin_date=start_date,
                             end_date=end_date)
    new_batch.save()

    # build insertion list
    insert_list = []
    for count, value in rising['query'].items():
        # only adds a kw if it doesn't exist in the db
        kw_id, created_bool = Keyword.objects.get_or_create(keyword=value)
        insert_list.append(BatchResult(batch=new_batch, keyword=kw_id, type="rising", frequency=rising['value'][count]))
    BatchResult.objects.bulk_create(insert_list)