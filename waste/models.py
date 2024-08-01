from django.db import models
from api.models import Image
from geography.models import GeoMarker
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class WasteReport(models.Model):
    class StatusChoice(models.TextChoices):
        CLEARED = "CLEARED", _("Waste Cleared")
        PENDING = "PENDING", _("Pending Removal")
        URGENT = "URGENT", _("Urgent Cleanup")

    status = models.CharField(
        max_length=20, choices=StatusChoice, default=StatusChoice.PENDING
    )
    description = models.TextField(
        _("Description"),
    )

    posted_by = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("Last modified"), auto_now=True)

    location = models.ForeignKey(to=GeoMarker, on_delete=models.DO_NOTHING)
    thumbnail = models.ForeignKey(to=Image, on_delete=models.DO_NOTHING)


class WasteReportActivity(models.Model):
    class ActivityType(models.TextChoices):
        CLEANUP = "CLEANUP", _("Waste Report Cleanup")
        UPDATE_POST = "UPDATE_POST", _("Updated a Post")
        ADD_POST = "ADD_POST", _("Added a Post")

    post = models.ForeignKey(to=WasteReport, on_delete=models.CASCADE)
    activity = models.CharField(
        _("Waste Report Activity"), max_length=20, choices=ActivityType
    )
    performed_by = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True)
    activity_timestamp = models.DateTimeField(
        _("Activity Timestamp"), auto_now_add=True
    )
