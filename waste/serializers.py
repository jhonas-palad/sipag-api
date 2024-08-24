from rest_framework import serializers
from .models import WasteReport, WasteReportActivity
from django.contrib.gis.geos import Point

from api.models import Image
from auth_api.serializers import UserDetailsSerailizer
from api.serializers import ImageSerializer
from django.contrib.auth import get_user_model


# from django.contrib.gis.db.models.proxy import SpatialProxy
# django.contrib.gis.db.models.proxy.SpatialProxy


class LatLngSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    lng = serializers.DecimalField(max_digits=9, decimal_places=6)


class WasteReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteReport
        fields = "__all__"

    def validate(self, attrs):
        if self.instance:
            for k, v in attrs.items():
                setattr(self.instance, k, v)
            self.instance.full_clean()
        return attrs

    def to_representation(self, instance):
        thumbnail_obj = instance.thumbnail
        # user = UserModel.objects.get(pk=instance.posted_by)
        user_details = UserDetailsSerailizer(
            instance=instance.posted_by, context=self.context
        ).data
        cleaner_details = None
        if hasattr(instance, "cleaner") and instance.cleaner:
            cleaner_details = UserDetailsSerailizer(
                instance=instance.cleaner, context=self.context
            ).data
        instance = super().to_representation(instance)
        instance["location"] = {
            "lng": instance["location"]["coordinates"][0],
            "lat": instance["location"]["coordinates"][1],
        }
        instance["thumbnail"] = ImageSerializer(
            instance=thumbnail_obj, context=self.context
        ).data
        instance["posted_by"] = user_details
        instance["cleaner"] = cleaner_details
        return instance


class NewWasteReportSerializer(serializers.Serializer):
    description = serializers.CharField()
    title = serializers.CharField(max_length=255)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    image = serializers.ImageField()

    def create(self, validated_data):
        image = self.create_image_instance(validated_data.pop("image"))
        waste_report = WasteReport.objects.create(
            title=validated_data.pop("title"),
            description=validated_data.pop("description"),
            location=Point(
                validated_data.pop("longitude"), validated_data.pop("latitude")
            ),
            posted_by=validated_data.pop("user_id"),
            thumbnail=image,
        )

        return waste_report

    def create_image_instance(self, image):
        img = Image(img_file=image)
        img.upload_to = "waste_reports"
        img.save()
        return img


class ActionWasteReportSerializer(serializers.Serializer):
    CHOICES = ("accept", "done", "cancel")
    cleaner = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all()
    )
    post_id = serializers.PrimaryKeyRelatedField(queryset=WasteReport.objects.all())
    action = serializers.ChoiceField(choices=CHOICES)

    def validate(self, attrs):
        waste_post = self.context.get("waste_post")

        if waste_post.posted_by == attrs["cleaner"]:
            raise serializers.ValidationError(
                {"cleaner": "You cannot accept waste report task to your own post"}
            )

        return attrs

    def validate_action(self, action):
        instance = self.context.get("waste_post")
        instance_status = instance.status

        if action == "accept" and instance_status != WasteReport.StatusChoice.AVAILABLE:
            raise serializers.ValidationError(
                "Waste report status is not available, can't accept the task"
            )
        return action


# class WasteActivitySerializer(serializers.ModelSerializer): ...
