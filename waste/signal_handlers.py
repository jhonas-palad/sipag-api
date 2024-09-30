from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from .signals import finished_task_post
from .serializers import (
    WasteActivitySerializer,
    CleanerPointsSerializer,
    WasteReportActivity,
)
from announcements.serializers import (
    PrivateAnnouncementSerializer,
    PublicAnnouncementSerializer,
)
from django.conf import settings

channel_layer = get_channel_layer()


@receiver(post_save, sender=WasteReportActivity)
def create_waste_report_activity(sender, instance, **kwargs):
    serializer = WasteActivitySerializer(instance=instance).data
    full_name = serializer["user"]["first_name"] + " " + serializer["user"]["last_name"]
    post_owner_id = serializer["post"]["posted_by"]["id"]
    if serializer["activity"] == WasteReportActivity.ActivityType.ADDED_POST:
        PrivateAnnouncementSerializer.create_system_announcements(
            title="ADDED_POST",
            description=f"{full_name} posted a waste report: {serializer['post']['title']}",
        )
    elif serializer["activity"] == WasteReportActivity.ActivityType.ACCEPT_TASK:
        PrivateAnnouncementSerializer.create_private_announcement(
            to=post_owner_id,
            title="Accepted Post",
            description=f"{full_name} accepted the waste report: {serializer['post']['title']}",
        )
    elif serializer["activity"] == WasteReportActivity.ActivityType.CANCEL_TASK:
        PrivateAnnouncementSerializer.create_private_announcement(
            to=post_owner_id,
            title="Cancelled Task",
            description=f"{full_name} cancel the task of waste report: {serializer['post']['title']}",
        )
    elif serializer["activity"] == WasteReportActivity.ActivityType.FINISHED_TASK:
        PrivateAnnouncementSerializer.create_private_announcement(
            to=post_owner_id,
            title="Finished Task",
            description=f"{full_name} finished the task of waste report: {serializer['post']['title']}",
        )

    # async_to_sync(channel_layer.group_send)(
    #     "public_wra_room", {"type": "send.notification", "message": serializer.data}
    # )


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
