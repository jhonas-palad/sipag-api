from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied, MethodNotAllowed
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import WasteReport, WasteReportActivity
from channels.db import database_sync_to_async
from .serializers import (
    NewWasteReportSerializer,
    WasteReportSerializer,
    ActionWasteReportSerializer,
)

from datetime import datetime


# Create your views here.
class WasteReportView(GenericAPIView):
    queryset = WasteReport.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = WasteReportSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    post_action = None

    def get_response(self, data, **kwargs):
        return Response(data=data, status=status.HTTP_201_CREATED, **kwargs)

    def get_waste_report(self, id=None, **kwargs):
        try:
            return WasteReport.objects.get(pk=id)
        except WasteReport.DoesNotExist:
            raise NotFound(f"Waste report with id {id}, doesn't exists.")

    def get_waste_reports(self):
        if self.lookup_field in self.kwargs:
            return self.get_object(), False

        return self.get_queryset(), True

    def get(self, request, *args, **kwargs):

        data, many = self.get_waste_reports()
        result = self.get_serializer(instance=data, many=many).data
        return Response(data=result, status=status.HTTP_200_OK)

    def create_waste_report(self, data):
        serializer = NewWasteReportSerializer(
            data=data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        result = self.get_serializer(instance=result).data
        return result

    def post(self, request, *args, **kwargs):
        """
        Create a new post

        Don't allow when there is a pk in kwargs
        """

        if "pk" in kwargs:
            raise MethodNotAllowed(method="post")

        user = request.user
        data = request.data.dict()
        print(data)
        data["user_id"] = user.id

        waste_report = self.create_waste_report(data)
        return self.get_response(waste_report)

    def delete_wate_report(self, id):
        # waste_report = self.get_waste_reports(id=id, posted_by=self.user)
        waste_report = self.get_waste_report(id)
        print(waste_report)
        if waste_report.posted_by != self.user:
            raise PermissionDenied(
                "You don't have permission to delete this waste report."
            )
        waste_report.delete()
        return waste_report

    def delete(self, request, *args, **kwargs):
        self.user = request.user
        r = self.delete_wate_report(kwargs.pop("pk"))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs): ...


waste_report_view = WasteReportView.as_view()
# class WasteReportTasks(GenericAPIView):
#     queryset = WasteReport.objects.all()
#     serializer_class = NewWasteReportSerializer
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (JWTAuthentication,)
#     def accept_task(self, *args, **kwargs):
#         serializer = self.get_
#     def post(self, request, *args, **kwargs):


class WasteReportTaskView(GenericAPIView):
    queryset = WasteReportActivity.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def modify_post_task(self, data):
        data["cleaner"] = data["user"].id
        post_id = self.kwargs.get("post_id")
        instance = get_object_or_404(WasteReport.objects.all(), pk=post_id)

        data["post_id"] = post_id

        task_serializer = ActionWasteReportSerializer(
            data=data, context={"waste_post": instance}
        )
        task_serializer.is_valid(raise_exception=True)
        data = task_serializer.data

        if data["action"] == "accept":
            data = {
                "cleaner": data["cleaner"],
                "accepted_at": datetime.now(),
                "status": WasteReport.StatusChoice.INPROGRESS,
            }
        elif data["action"] == "done":
            data = {
                "cleaner": data["cleaner"],
                "completed_at": datetime.now(),
                "status": WasteReport.StatusChoice.CLEARED,
            }
        else:
            data = {
                "cleaner": None,
                "accepted_at": None,
                "status": WasteReport.StatusChoice.AVAILABLE,
            }
        serializer = WasteReportSerializer(instance=instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def post(self, request, *args, **kwargs):
        user = request.user
        request.data["user"] = user
        self.modify_post_task(request.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


waste_report_task_view = WasteReportTaskView.as_view()
