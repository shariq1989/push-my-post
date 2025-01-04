from django.core.management.base import BaseCommand, CommandError
from social_publish.service import suggest_pinterest_boards, get_pinterest_user_data, suggest_pinterest_boards
from site_scan.models import BlogPost
from social_publish.models import PinUser


class Command(BaseCommand):
    help = 'Save pinterest board suggestions for a users blog posts'

    def handle(self, *args, **options):
        suggest_boards()


def suggest_boards():
    # Fetch blog posts
    blog_posts = BlogPost.objects.all()
    print(f"Total blog posts to process: {blog_posts.count()}")

    try:
        pin_user = PinUser.objects.get(user__username='shariq1989')
    except PinUser.DoesNotExist:
        print("No PinUser found for username shariq1989")
        return  # Exit the method if no PinUser exists

    try:
        # Fetch Pinterest boards
        boards = get_pinterest_user_data(pin_user)
        print(f"Total Pinterest boards to compare: {len(boards)}")
    except Exception as e:
        print(f"Error fetching Pinterest boards: {e}")
        return  # Exit if board fetching fails

    # Batch processing with error handling for each blog post
    for blog_post in blog_posts:
        try:
            # Generate suggestions
            suggestions = suggest_pinterest_boards(
                blog_post,
                boards,
                min_confidence=0.5,
                max_suggestions=3
            )
            # Save suggestions to database
            print(f"Suggestions for blog post {blog_post.id}: {suggestions}")
            # ¸save_board_suggestions(blog_post, suggestions)
        except Exception as e:
            print(f"Error processing blog post {blog_post.id}: {e}")
            # Continue to next blog post if one fails
            continue
