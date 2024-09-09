from django.core.management.base import BaseCommand, CommandError
from site_scan.service import parse_sitemap
from site_scan.models import Site, BlogPost


class Command(BaseCommand):
    help = 'Update blog posts for a site.'

    def handle(self, *args, **options):
        # Get all BlogPosts where the associated Site's URL contains "jamilghar"
        blogposts_to_delete = BlogPost.objects.filter(site__url__icontains='jamilghar')

        # Delete the selected BlogPosts
        blogposts_to_delete.delete()

        self.stdout.write(self.style.SUCCESS('Successfully deleted posts with Site URL containing "jamilghar"'))
        posts = parse_sitemap('https://jamilghar.com', False)
