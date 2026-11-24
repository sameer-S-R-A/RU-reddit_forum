from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from kshitiz_kumar.accounts.models import Profile
from aaditya_verma.communities.models import Community
from saksham_yadav.posts.models import Post, PostMedia
from aditya_kumar.interactions.models import Comment, Vote
from aditya_kumar.messaging.models import Conversation, DirectMessage
from .insforge import get_insforge
from .sync import profile_saved, community_saved, post_saved, comment_saved, vote_saved, conversation_saved, message_saved

@receiver(post_save, sender=Profile)
def sync_profile(sender, instance, **kwargs): profile_saved(instance)
@receiver(post_save, sender=Community)
def sync_community(sender, instance, **kwargs): community_saved(instance)
@receiver(m2m_changed, sender=Community.members.through)
def sync_members(sender, instance, action, **kwargs):
    if action.startswith("post_"): community_saved(instance)
@receiver(post_save, sender=Post)
def sync_post(sender, instance, **kwargs): post_saved(instance)
@receiver(post_save, sender=PostMedia)
def sync_media(sender, instance, **kwargs): post_saved(instance.post)
@receiver(post_save, sender=Comment)
def sync_comment(sender, instance, **kwargs): comment_saved(instance)
@receiver(post_save, sender=Vote)
def sync_vote(sender, instance, **kwargs): vote_saved(instance)
@receiver(post_delete, sender=Vote)
def remove_vote(sender, instance, **kwargs):
    try: get_insforge().delete("reddit_votes", {"post_local_id": instance.post_id, "username": instance.user.username})
    except Exception: pass
@receiver(post_save, sender=Conversation)
def sync_conversation(sender, instance, **kwargs): conversation_saved(instance)
@receiver(m2m_changed, sender=Conversation.participants.through)
def sync_conversation_members(sender, instance, action, **kwargs):
    if action.startswith("post_"): conversation_saved(instance)
@receiver(post_save, sender=DirectMessage)
def sync_message(sender, instance, **kwargs): message_saved(instance)
