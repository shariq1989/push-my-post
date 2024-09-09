from django.core.management.base import BaseCommand, CommandError
from social_publish.service import create_tweet


class Command(BaseCommand):
    help = 'Create tweets for Jamil Ghar'

    def handle(self, *args, **options):
        tweet_data = {
            "text": "Hello Twitter! This is a tweet from my automated script."
        }
        create_tweet(tweet_data)
        response = create_tweet(tweet_data)
        print(response)
