from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        extra_kwargs = {
            "img_file": {"use_url": True},
            "id": {"required": False},
            "hash": {"allow_blank": True, "required": False},
        }
