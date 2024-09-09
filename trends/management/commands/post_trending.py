from django.core.management.base import BaseCommand, CommandError
import time
from pytz import timezone
from datetime import date, datetime, timedelta

from trends.models import BatchRequest, BatchResult, Keyword
from trends.service import trends_standard_post, store_trends_post


class Command(BaseCommand):
    help = 'POST request for Google Trends to DataforSEO'

    def handle(self, *args, **options):
        # get trends over the past five days
        tz = timezone('EST')
        end_date = datetime.now(tz)
        begin_date = end_date - timedelta(5)
        trending_results = trends_standard_post(begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        store_trends_post(trending_results)

        res_time = trending_results['time']
        res_id = trending_results['tasks'][0]['id']
        res_data = trending_results['tasks'][0]['data']
        message = 'POST Trending successful. Time: {}, id: {}, data: {}'.format(res_time, res_id, res_data)
        self.stdout.write(self.style.SUCCESS(message))
