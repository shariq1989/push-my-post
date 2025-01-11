from django.core.management.base import BaseCommand, CommandError
from social_publish.service import suggest_pinterest_boards, get_pinterest_user_data, precompute_board_embeddings
from site_scan.models import BlogPost, PinterestBoardSuggestion
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
        pin_user = PinUser.objects.get(user__username='shariq1989@gmail.com')
    except PinUser.DoesNotExist:
        print("No PinUser found for username shariq1989")
        return

    try:
        # Fetch Pinterest boards
        boards = get_pinterest_user_data(pin_user)
        print(f"Total Pinterest boards to compare: {len(boards)}")
    except Exception as e:
        print(f"Error fetching Pinterest boards: {e}")
        return

    # Precompute board embeddings
    try:
        board_embeddings = precompute_board_embeddings(boards)
        print(f"Precomputed embeddings for {len(board_embeddings)} boards.")
    except Exception as e:
        print(f"Error computing board embeddings: {e}")
        return

    # Delete old suggestions
    PinterestBoardSuggestion.objects.all().delete()

    # Process blog posts
    for blog_post in blog_posts:
        try:
            suggestions = suggest_pinterest_boards(
                blog_post,
                board_embeddings,
                min_confidence=0.5,
                max_suggestions=3,
            )
            # Save suggestions to database
            for suggestion in suggestions:
                PinterestBoardSuggestion.objects.create(
                    blog_post=blog_post,
                    board_id=suggestion["board_id"],
                    board_name=suggestion["board_name"],
                    match_score=suggestion["match_score"],
                )
            print(f"Suggestions for blog post {blog_post.title}: {suggestions}")
        except Exception as e:
            print(f"Error processing blog post {blog_post.title}: {e}")
            continue
