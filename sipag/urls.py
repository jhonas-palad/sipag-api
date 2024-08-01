from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, re_path, include
from django.views import defaults
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status


print(defaults.page_not_found)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^api/v1/", include("api.urls", namespace="v1")),
    # re_path(r'v2')
]

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {
                "document_root": settings.MEDIA_ROOT,
            },
        ),
    ]
