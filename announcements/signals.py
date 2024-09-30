from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings


from .serializers import PublicAnnouncementSerializer, PrivateAnnouncementSerializer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


import functools

channel_layer = get_channel_layer()


def handler(serializer_cls, group_name):
    # @functools.wraps()
    def inner(sender, instance, *args, **kwargs):
        serializer = serializer_cls(instance=instance)
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "send.notification", "message": serializer.data},
        )

    return inner


public_announcement_signal_handler = handler(
    PublicAnnouncementSerializer,
    settings.SIPAG_CONFIG["CONSUMER_GROUPS"]["announcements"],
)
receiver(post_save, sender="announcements.PublicAnnouncement")(
    public_announcement_signal_handler
)

private_announcement_signal_handler = handler(
    PrivateAnnouncementSerializer,
    settings.SIPAG_CONFIG["CONSUMER_GROUPS"]["announcements"],
)
receiver(post_save, sender="announcements.PrivateAnnouncement")(
    private_announcement_signal_handler
)

# IMPORT THIS MODULE IN APP