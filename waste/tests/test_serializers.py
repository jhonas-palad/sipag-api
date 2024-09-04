from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.conf import settings
from phonenumbers import PhoneNumber

from rest_framework import serializers

from ..models import WasteReport, WasteReportActivity
from ..serializers import NewWasteReportSerializer, ActionWasteReportSerializer

UserModel = get_user_model()


class SerializersTest(TestCase):

    def create_post(self, user):
        image_file_raw = open("./media/waste_reports/stairs-to-bldg.jpg", "rb")
        image_file = ImageFile(image_file_raw)

        new = NewWasteReportSerializer(
            data={
                "title": "test Title",
                "description": "test Description",
                "user_id": user.pk,
                "latitude": "12.1221",
                "longitude": "123.2332",
                "image": image_file,
            }
        )
        new.is_valid(raise_exception=True)
        # image_file_raw.close()
        return new.save()

    def create_user(self, **credentials):
        try:
            return UserModel.objects.get(phone_number=credentials.get("phone_number"))
        except:
            return UserModel.objects.create_user(
                **credentials, password="siMplePassword@123"
            )

    def test_accept_waste_report_task(self):
        user1 = self.create_user(phone_number=PhoneNumber("63", "09394961234"))
        user2 = self.create_user(phone_number=PhoneNumber("63", "09394961276"))

        new_waste_report = self.create_post(user2)

        serializer = ActionWasteReportSerializer(
            data={
                "action": "accept",
                "cleaner": user1.pk,
                "post_id": new_waste_report.pk,
            },
            context={"waste_post": new_waste_report},
        )

        self.assertTrue(
            serializer.is_valid(),
            msg=f"Invalid data form ActionWasteReportSerializer {serializer.errors}",
        )
        waste_report = serializer.save()["result"]

        self.assertEqual(
            waste_report.status,
            WasteReport.StatusChoice.INPROGRESS,
            msg=f"WasteReport status must be {WasteReport.StatusChoice.INPROGRESS}, once accepted ",
        )
