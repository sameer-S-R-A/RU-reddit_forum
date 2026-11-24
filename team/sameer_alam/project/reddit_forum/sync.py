"""Mirror forum records into InsForge so shared forum data persists remotely."""
from .insforge import get_insforge


def _safe(fn):
    try:
        fn()
    except Exception:
        # A temporary backend outage must not lose the local transaction.
        # The exception is intentionally not exposed to end users.
        pass


def profile_saved(profile):
    _safe(lambda: get_insforge().upsert("reddit_profiles", {
        "local_user_id": profile.user_id, "insforge_user_id": str(profile.insforge_user_id) if profile.insforge_user_id else None,
        "username": profile.user.username, "email": profile.user.email, "bio": profile.bio, "avatar_url": profile.avatar_url,
    }))


def community_saved(community):
    _safe(lambda: get_insforge().upsert("reddit_communities", {
        "local_id": community.id, "name": community.name, "slug": community.slug, "description": community.description,
        "owner_username": community.owner.username, "member_usernames": list(community.members.values_list("username", flat=True)),
    }))


def post_saved(post):
    _safe(lambda: get_insforge().upsert("reddit_posts", {
        "local_id": post.id, "community_local_id": post.community_id, "author_username": post.author.username,
        "post_type": post.post_type, "title": post.title, "body": post.body, "link_url": post.link_url,
        "media_urls": [item.image.url for item in post.media.all()],
    }))


def comment_saved(comment):
    _safe(lambda: get_insforge().upsert("reddit_comments", {
        "local_id": comment.id, "post_local_id": comment.post_id, "author_username": comment.author.username, "body": comment.body,
    }))


def vote_saved(vote):
    _safe(lambda: get_insforge().upsert("reddit_votes", {
        "post_local_id": vote.post_id, "username": vote.user.username, "value": vote.value,
    }))


def conversation_saved(conversation):
    _safe(lambda: get_insforge().upsert("reddit_conversations", {
        "local_id": conversation.id, "participant_usernames": list(conversation.participants.values_list("username", flat=True)),
    }))


def message_saved(message):
    _safe(lambda: get_insforge().upsert("reddit_messages", {
        "local_id": message.id, "conversation_local_id": message.conversation_id,
        "sender_username": message.sender.username, "body": message.body,
    }))
