from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from api.models import Image

# Create your models here.


class GeoMarker(models.Model):
    location = models.PointField(_("location"), geography=True, default=Point(0.0, 0.0))
    image = models.ForeignKey(to=Image, on_delete=models.DO_NOTHING)
