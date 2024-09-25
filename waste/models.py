from django.db import models
from api.models import Image
from auth_api.validators import admin_user_validator
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, F, CheckConstraint
from django.conf import settings
from django.core.validators import MaxValueValidator


User = get_user_model()


class WasteReport(models.Model):
    class StatusChoice(models.TextChoices):
        CLEARED = "CLEARED", _("waste cleared")
        INPROGRESS = "INPROGRESS", _("in progress")
        AVAILABLE = "AVAILABLE", _("available for cleanup")

    title = models.CharField(
        _("title"),
        max_length=255,
    )
    status = models.CharField(
        _("status"), max_length=20, choices=StatusChoice, default=StatusChoice.AVAILABLE
    )
    description = models.TextField(
        _("description"),
    )

    posted_by = models.ForeignKey(to=User, on_delete=models.CASCADE)
    cleaner = models.ForeignKey(
        to=User,
        related_name="wastereport_cleaners",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    last_modified = models.DateTimeField(_("Last modified"), auto_now=True)
    completed_at = models.DateTimeField(_("completed at"), blank=True, null=True)
    accepted_at = models.DateTimeField(_("accepted at"), blank=True, null=True)
    location = models.PointField(_("location"), geography=True, default=Point(0.0, 0.0))
    thumbnail = models.ForeignKey(to=Image, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            CheckConstraint(
                name="no_self_post_accept_task", check=~Q(posted_by=F("cleaner"))
            )
        ]


class WasteReportActivity(models.Model):
    class ActivityType(models.TextChoices):
        ACCEPT_TASK = "ACCEPT_POST", _("Accepted post")
        CANCEL_TASK = "CANCEL_TASK", _("Cancelled task")
        FINISHED_TASK = "FINISH_TASK", _("Finish task")
        UPDATED_POST = "UPDATED_POST", _("Updated a Post")
        ADDED_POST = "ADDED_POST", _("Added a Post")

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True)
    post = models.ForeignKey(to=WasteReport, on_delete=models.SET_NULL, null=True)
    activity = models.CharField(
        _("Waste Report Activity"), max_length=20, choices=ActivityType
    )
    activity_timestamp = models.DateTimeField(
        _("Activity Timestamp"), auto_now_add=True
    )

    class Meta:
        ordering = ["-activity_timestamp"]


points_validator = MaxValueValidator(settings.SIPAG_CONFIG["MAX_POINTS"])


# I should have created a new variant of user.
class CleanerPoints(models.Model):
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, blank=True, primary_key=True
    )
    count = models.IntegerField(
        _("points count"), default=0, validators=[points_validator]
    )
    redeemed = models.BooleanField(_("points redemed"), default=False)


class RedeemRecord(models.Model):
    cleaner_points = models.ForeignKey(
        to=CleanerPoints, on_delete=models.CASCADE, blank=True
    )
    claimed_date = models.DateTimeField(_("claimed date"), auto_now_add=True)
    assisted_by = models.ForeignKey(
        to=User,
        related_name="points_assisted_by",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def clean(self) -> None:
        if not self.assisted_by.is_staff:
            raise ValidationError({"assisted_by": "Only staff can redeem points"})
        return super().clean()
