from django.db import models
from django.utils.translation import gettext_lazy as _


class WastePost:
    description = models.TextField(
        verbose_name=_("Description"), blank=False, default=""
    )
