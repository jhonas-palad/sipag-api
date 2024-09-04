import blurhash
from PIL import Image as PIL_Image

from django.db import models
from django.utils.translation import gettext_lazy as _
import os


def upload_to(instance, file):
    return os.path.join(instance.upload_to or "qwe", file)


class Image(models.Model):

    img_file = models.ImageField(
        _("image file"), upload_to=upload_to, blank=True, default=""
    )
    hash = models.CharField(_("image hash"), max_length=100, blank=True, default="")

    def __repr__(self):
        return f"Image {self.id} - {self.img_file.name}"

    __str__ = __repr__

    def hash_image(self):
        with PIL_Image.open(self.img_file.file) as image:
            image.thumbnail((100, 100))
            hash = blurhash.encode(image, x_components=4, y_components=3)
            return hash

    def get_image_url(self):
        return self.img_file.url

    def save(self, *args, **kwargs):
        if not hasattr(self, "upload_to"):
            self.upload_to = ""
        self.hash = self.hash_image()
        return super().save(*args, **kwargs)

    @classmethod
    def save_img_file_to(cls, image, upload_to="others"):
        img = cls(img_file=image)
        img.upload_to = upload_to
        img.save()
        return img
