from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from .signals import finished_task_post
from .serializers import WasteActivitySerializer, CleanerPointsSerializer
from announcements.serializers import PrivateAnnouncementSerializer
from django.conf import settings

channel_layer = get_channel_layer()


@receiver(post_save, sender="waste.WasteReportActivity")
def create_waste_report_activity(sender, instance, **kwargs):
    serializer = WasteActivitySerializer(instance=instance)
    async_to_sync(channel_layer.group_send)(
        "public_wra_room", {"type": "send.notification", "message": serializer.data}
    )


@receiver(post_save, sender="waste.RedeemRecord")
def reset_points(sender, instance, **kwargs):
    CleanerPointsSerializer.reset_points(instance.cleaner_points)
    private_announcement = PrivateAnnouncementSerializer.create_private_announcement(
        to=instance.cleaner_points.user.pk,
        title="Congratulations",
        description="Redeemed points",
    )

    


@receiver(finished_task_post)
def generate_points(sender, cleaner, **kwargs):
    CleanerPointsSerializer.generate_points(cleaner=cleaner)
