from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import PrivateAnnouncement, PublicAnnouncement
from .serializers import (
    PublicAnnouncementSerializer,
    PrivateAnnouncementSerializer,
    AnnouncementSerializer,
)
from itertools import chain
from operator import attrgetter


# Create your views here.
class PublicAnnouncementView(ListCreateAPIView):
    queryset = PublicAnnouncement.objects.all()
    serializer_class = PublicAnnouncementSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if not "by" in request.data:
            request.data["by"] = request.user.id
        return super().post(request=request, *args, **kwargs)


public_announcement_view = PublicAnnouncementView.as_view()


class PrivateAnnouncementView(ListCreateAPIView):
    queryset = PrivateAnnouncement.objects.all()
    serializer_class = PrivateAnnouncementSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    filterset_fields = [
        "to",
    ]


private_announcement_view = PrivateAnnouncementView.as_view()


class AnnouncementView(GenericAPIView):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = AnnouncementSerializer

    def get_to(self):
        to = self.request.query_params.get("to", None)
        try:
            to = int(to)
        except:
            to = None
        return to

    def get(self, request, *args, **kwargs):
        to = self.get_to()

        qs1 = PublicAnnouncement.objects.all().order_by("-date_created")
        if to:
            qs2 = (
                PrivateAnnouncement.objects.all()
                .filter(to=to)
                .order_by("-date_created")
            )
        else:
            qs2 = PrivateAnnouncement.objects.all().filter().order_by("-date_created")

        l = list(sorted(chain(qs1, qs2), key=attrgetter("date_created"), reverse=True))
        s = AnnouncementSerializer(instance=l, many=True)

        return Response(data=s.data, status=status.HTTP_200_OK)


announcement_view = AnnouncementView.as_view()
