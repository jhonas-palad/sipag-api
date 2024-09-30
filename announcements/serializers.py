from rest_framework import serializers
from .models import PrivateAnnouncement, PublicAnnouncement, PushToken
from django.contrib.auth import get_user_model
from .tasks import send_push_message, send_push_messages

UserModel = get_user_model()

# class BaseNotificationSerializer(serializers.ModelSerializer):


class PrivateAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateAnnouncement
        fields = "__all__"

    @classmethod
    def create_private_announcement(cls, to, title, description):
        serializer = cls(data={"title": title, "description": description, "to": to})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_push_message.delay_on_commit(to, description)

        return serializer.data

    @classmethod
    def create_system_announcements(cls, title, description):
        serializer = cls(data={"title": title, "description": description})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_push_messages.delay_on_commit(description)

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


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = "__all__"
