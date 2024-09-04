from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from .serializers import WasteActivitySerializer

channel_layer = get_channel_layer()


@receiver(post_save, sender="waste.WasteReportActivity")
def create_waste_report_activity(sender, instance, **kwargs):
    serializer = WasteActivitySerializer(instance=instance)
    async_to_sync(channel_layer.group_send)(
        "public_wra_room", {"type": "send.notification", "message": serializer.data}
    )
