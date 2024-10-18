from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

UserModel = get_user_model()


# Create your models here.
class NotficationBase(models.Model):
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))
    date_created = models.DateTimeField(_("date create"), auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-date_created"]


class PublicAnnouncement(NotficationBase):
    by = models.ForeignKey(to=UserModel, on_delete=models.PROTECT)

    def clean(self) -> None:
        if not self.by.is_staff:
            raise ValidationError({"by": f"Only staff can create a {self.__class__}"})
        return super().clean()


class PrivateAnnouncement(NotficationBase):
    to = models.ForeignKey(to=UserModel, on_delete=models.CASCADE, null=True)

    class Codes(models.TextChoices):
        WASTE = ("WASTE", _("Waste"))
        POINTS = ("POINTS", _("Points"))
        ANNOUNCEMENTS = ("ANNOUNCEMENTS", _("Announcements"))

    code = models.CharField(_("code"), choices=Codes, null=True)
    code_entity_id = models.IntegerField(_("code entity id"), blank=True, null=True)


class SystemNotification(NotficationBase): ...


class PushToken(models.Model):
    user = models.ForeignKey(to=UserModel, on_delete=models.CASCADE)
    token = models.CharField(_("token"), max_length=255, blank=False, null=False)
    active = models.BooleanField(_("active"), default=True)
    registered_date = models.DateTimeField(_("registered data"), auto_now_add=True)
