from django.core.management.base import BaseCommand, CommandError

from trends.models import BatchRequest, BatchResult, Keyword
from trends.service import trends_standard_get, calling_live_trends


class Command(BaseCommand):
    help = 'GET request for Google Trends to DataforSEO'

    def handle(self, *args, **options):
        resp = trends_standard_get()
        if not resp[0]:
            self.stdout.write(self.style.ERROR(resp[1]))
            self.stdout.write(self.style.NOTICE('Standard Trends method failed. Using Live method.'))
            calling_live_trends()
        else:
            message = 'GET Trending completed.'
            self.stdout.write(self.style.SUCCESS(message[1]))
