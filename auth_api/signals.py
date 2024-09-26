from django.dispatch import receiver
from django.db.models.signals import post_save
from waste.serializers import CleanerPointsSerializer


@receiver(post_save, sender="auth_api.User")
def create_waste_report_activity(sender, instance, **kwargs):
    if not instance.is_staff:
        CleanerPointsSerializer.generate_points(instance)
