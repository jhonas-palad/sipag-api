from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve
from django.urls import path, re_path, include


def index_view(request):
    return HttpResponse("Hello, world!")


urlpatterns = [
    path("index/", index_view),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls", namespace="v1")),
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
