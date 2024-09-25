from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http.response import Http404
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    get_object_or_404,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import (
    NotFound,
    MethodNotAllowed,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import WasteReport, WasteReportActivity, CleanerPoints, RedeemRecord
from .serializers import (
    NewWasteReportSerializer,
    WasteActivitySerializer,
    WasteReportSerializer,
    ActionWasteReportSerializer,
    DeleteWasteReportSerializer,
    CleanerPointsSerializer,
    RedeemRecordSerializer,
)

from .helpers import generate_cleaner_points
from datetime import datetime

UserModel = get_user_model()


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
        data["user_id"] = user.id

        waste_report = self.create_waste_report(data)
        return self.get_response(waste_report)

    def delete_waste_report(self, id):
        # waste_report = self.get_waste_report(id)
        waste_report = DeleteWasteReportSerializer(
            data={"waste_report": id}, context=self.get_serializer_context()
        )
        waste_report.is_valid(raise_exception=True)
        waste_report.delete()

    def delete(self, request, *args, **kwargs):
        self.user = request.user
        self.delete_waste_report(kwargs.pop("pk"))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs): ...


waste_report_view = WasteReportView.as_view()


class WasteReportTaskView(GenericAPIView):
    queryset = WasteReportActivity.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def modify_post_task(self, data):
        data["cleaner"] = data["user"].id
        data["post_id"] = self.kwargs.get("post_id")
        instance = get_object_or_404(WasteReport.objects.all(), pk=data["post_id"])

        task_serializer = ActionWasteReportSerializer(
            data=data, context={"waste_post": instance, **self.get_serializer_context()}
        )
        task_serializer.is_valid(raise_exception=True)
        task_serializer.save()
        data = task_serializer.data

        return data

    def post(self, request, *args, **kwargs):
        user = request.user
        request.data["user"] = user
        data = self.modify_post_task(request.data)
        return Response(data=data, status=status.HTTP_202_ACCEPTED)


waste_report_task_view = WasteReportTaskView.as_view()


class WasteReportActivitesView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = WasteReportActivity.objects.all()
    serializer_class = WasteActivitySerializer


waste_report_activities_view = WasteReportActivitesView.as_view()


class CleanerRetrieveView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (JWTAuthentication,)
    queryset = CleanerPoints.objects.all()
    serializer_class = CleanerPointsSerializer
    # lookup_field = "id"

    def get_object(self):
        try:
            result = super().get_object()
            return result
            # return super().get_object()
        except Http404 as exc:
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
            return generate_cleaner_points(**filter_kwargs)


cleaner_retrieve_view = CleanerRetrieveView.as_view()


class RedeemRecordView(CreateAPIView, ListAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = (JWTAuthentication,)
    queryset = RedeemRecord.objects.all()
    serializer_class = RedeemRecordSerializer
    filterset_fields = [
        "cleaner_points",
    ]

    def post(self, request, *args, **kwargs):
        request.data["assisted_by"] = request.user.id
        return super().post(request, *args, **kwargs)


redeem_record_view = RedeemRecordView.as_view()
