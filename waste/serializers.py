from datetime import datetime
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model
from django.db.models.query import Q
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from auth_api.serializers import UserDetailsSerailizer, UserSerializer
from api.serializers import ImageSerializer
from api.models import Image
from .signals import finished_task_post
from .models import WasteReport, WasteReportActivity, CleanerPoints, RedeemRecord

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
        image = Image.save_img_file_to(
            validated_data.pop("image"), upload_to="waste_reports"
        )
        user = validated_data.pop("user_id") or self.context.request.user

        waste_report = WasteReport.objects.create(
            title=validated_data.pop("title"),
            description=validated_data.pop("description"),
            location=Point(
                validated_data.pop("longitude"), validated_data.pop("latitude")
            ),
            posted_by=user,
            thumbnail=image,
        )

        WasteActivitySerializer.create_waste_activity(
            user=user.pk,
            post=waste_report.pk,
            activity=WasteReportActivity.ActivityType.ADDED_POST,
        )

        return waste_report


class DeleteWasteReportSerializer(serializers.Serializer):
    waste_report = serializers.PrimaryKeyRelatedField(
        queryset=WasteReport.objects.all(), write_only=True
    )

    def validate_waste_report(self, waste_report):
        user = self.context.get("request").user

        if not user.is_staff and waste_report.posted_by != user:
            raise PermissionDenied(
                "You don't have permission to delete this waste report."
            )
        if waste_report.status != WasteReport.StatusChoice.AVAILABLE:
            raise serializers.ValidationError(
                f"Waste report's status is {waste_report.status}, can't delete this post."
            )
        return waste_report

    def delete(self):
        waste_report = self.validated_data["waste_report"]
        waste_report.delete()


class ActionWasteReportSerializer(serializers.Serializer):
    CHOICES = ("accept", "done", "cancel")
    cleaner = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), write_only=True
    )
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=WasteReport.objects.all(), write_only=True
    )
    action = serializers.ChoiceField(choices=CHOICES)
    result = WasteReportSerializer(read_only=True, required=False)

    def validate(self, attrs):
        waste_post = self.context.get("waste_post")
        if attrs["action"] == "accept" and waste_post.cleaner:
            raise serializers.ValidationError(
                "Someone already accepted this waste report"
            )
        return attrs

    def validate_cleaner(self, cleaner):
        waste_post = self.context.get("waste_post")
        if waste_post.posted_by == cleaner:
            raise serializers.ValidationError(
                "You cannot accept waste report task to your own post"
            )

        return cleaner

    def validate_action(self, action):
        instance = self.context.get("waste_post")
        instance_status = instance.status

        if action == "accept" and instance_status != WasteReport.StatusChoice.AVAILABLE:
            raise serializers.ValidationError(
                "Waste report status is not available, can't accept the task"
            )
        if (
            action == "cancel"
            and instance_status != WasteReport.StatusChoice.INPROGRESS
        ):
            raise serializers.ValidationError(
                f"Waste report status was {instance.status}, can't cancel the task"
            )
        if action == "done" and instance_status != WasteReport.StatusChoice.INPROGRESS:
            raise serializers.ValidationError(
                f"Waste report status was {instance.status}, can't finish the task"
            )

        return action

    def create(self, validated_data):
        cleaner = validated_data["cleaner"]
        if validated_data["action"] == "accept":
            activity = WasteReportActivity.ActivityType.ACCEPT_TASK
            data = {
                "cleaner": validated_data["cleaner"].pk,
                "accepted_at": datetime.now(),
                "status": WasteReport.StatusChoice.INPROGRESS,
            }
        elif validated_data["action"] == "done":
            activity = WasteReportActivity.ActivityType.FINISHED_TASK
            data = {
                "cleaner": validated_data["cleaner"].pk,
                "completed_at": datetime.now(),
                "status": WasteReport.StatusChoice.CLEARED,
            }
            # finished_task_post.send(self.__class__, cleaner=cleaner)
            CleanerPointsSerializer.add_points(cleaner=cleaner)

        else:
            activity = WasteReportActivity.ActivityType.CANCEL_TASK
            data = {
                "cleaner": None,
                "accepted_at": None,
                "status": WasteReport.StatusChoice.AVAILABLE,
            }

        serializer = WasteReportSerializer(
            instance=self.context.get("waste_post"), data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        waste_report = serializer.save()

        WasteActivitySerializer.create_waste_activity(
            user=cleaner.pk, post=waste_report.pk, activity=activity
        )

        return {"result": waste_report, "action": validated_data["action"]}


class WasteActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteReportActivity
        fields = "__all__"

    def to_representation(self, initial_instance):
        user_details = UserDetailsSerailizer(
            instance=initial_instance.user, context=self.context
        ).data
        if initial_instance.post:
            post_details = WasteReportSerializer(
                instance=initial_instance.post, context=self.context
            ).data
        else:
            post_details = None

        instance = super().to_representation(initial_instance)
        instance["user"] = user_details
        instance["post"] = post_details
        return instance

    @classmethod
    def create_waste_activity(cls, **kwargs):
        """
        Helper function to create a WasteReportActivity
        """
        serializer = cls(data=kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.save()


class CleanerPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleanerPoints
        fields = "__all__"

    def validate(self, attrs):
        if self.instance:
            if self.instance.count > settings.SIPAG_CONFIG["MAX_POINTS"]:
                raise serializers.ValidationError(
                    {
                        "count": "User has reached the maximum points, redeem it first to reset."
                    }
                )

        return super().validate(attrs)

    def to_representation(self, instance):

        user = UserSerializer(instance=instance.user, context=self.context).data
        return {
            "user": user,
            "count": instance.count,
            "redeemed": instance.redeemed,
        }

    @classmethod
    def add_points(cls, cleaner):
        cleaner_points = get_object_or_404(cls.Meta.model.objects.all(), user=cleaner)

        serializer = cls(
            instance=cleaner_points,
            data={"count": cleaner_points.count + 1},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @classmethod
    def reset_points(cls, cleaner):
        cleaner_points = get_object_or_404(cls.Meta.model.objects.all(), user=cleaner)

        serializer = cls(
            instance=cleaner_points,
            data={"count": 0},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    @classmethod
    def generate_points(cls, cleaner):
        cleaner_points, new = cls.Meta.model.objects.get_or_create(user=cleaner)
        count = cleaner.wastereportactivity_set.filter(
            activity=WasteReportActivity.ActivityType.FINISHED_TASK
        ).count()

        serializer = cls(instance=cleaner_points, data={"count": count}, partial=True)
        serializer.is_valid(raise_exception=True)
        if new or cleaner_points.count != count:
            return serializer.save()

        return cleaner_points


class RedeemRecordSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        cleaner_points = CleanerPointsSerializer(
            instance=instance.cleaner_points, context=self.context
        ).data
        assisted_by = UserSerializer(
            instance=instance.assisted_by, context=self.context
        ).data

        return {
            "cleaner_points": cleaner_points,
            "assisted_by": assisted_by,
            "claimed_date": instance.claimed_date,
        }

    def validate(self, attrs):
        if attrs["cleaner_points"].count < settings.SIPAG_CONFIG["MAX_POINTS"]:
            raise serializers.ValidationError(
                {
                    "cleaner_points": f"The user must reach {settings.SIPAG_CONFIG['MAX_POINTS']} points before claiming it"
                }
            )

        if attrs["assisted_by"].is_staff is False:
            raise serializers.ValidationError(
                {"assisted_by": "Only staff can redeem points"}
            )
        if self.instance:
            self.instance.full_clean()

        return super().validate(attrs)

    class Meta:
        model = RedeemRecord
        fields = "__all__"
