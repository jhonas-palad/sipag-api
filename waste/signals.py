from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import WasteReport


@receiver(pre_save, sender=WasteReport)
def save_thumbnail(sender, instance, **kwargs):
    print("pre save ", sender, instance, kwargs)
