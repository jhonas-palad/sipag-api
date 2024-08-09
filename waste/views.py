from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import WasteReport
from .serializers import NewWasteReportSerializer, WasteReportSerializer


# Create your views here.
class WasteReportView(GenericAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = WasteReportSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_response(self, data, **kwargs):
        return Response(data=data, status=status.HTTP_201_CREATED, **kwargs)

    def get_waste_report(self, id=None):
        try:
            return WasteReport.objects.get(pk=id)
        except WasteReport.DoesNotExist:
            raise NotFound(f"Waste report with id {id}, doesn't exists.")

    def get_waste_reports(self):
        return WasteReport.objects.all()

    def get(self, request, *args, **kwargs):
        many: bool
        if _id := kwargs.pop("id", None):
            data = self.get_waste_report(_id)
            many = False
        else:
            data = self.get_waste_reports()
            many = True
        result = self.get_serializer(instance=data, many=many).data
        return Response(data=result, status=status.HTTP_200_OK)

    def save_waste_report(self):
        result = self.serializer.save()
        result = self.get_serializer(instance=result).data
        return result

    def post(self, request, *args, **kwargs):
        user = request.user
        request.data["user_id"] = user.id
        print(request.data)
        self.serializer = NewWasteReportSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        self.serializer.is_valid(raise_exception=True)
        data = self.save_waste_report()
        return self.get_response(data)


waste_report_view = WasteReportView.as_view()
