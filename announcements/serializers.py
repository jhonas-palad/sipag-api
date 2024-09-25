from rest_framework import serializers
from .models import PrivateAnnouncement, PublicAnnouncement
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class PrivateAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateAnnouncement
        fields = "__all__"

    @classmethod
    def create_private_announcement(cls, to, title, description):
        serializer = cls(data={"title": title, "description": description, "to": to})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data


class PublicAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicAnnouncement
        fields = "__all__"


class AnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    date_created = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    by = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(), required=False
    )
    to = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(), required=False
    )
