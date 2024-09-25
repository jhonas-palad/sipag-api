from django.urls import path, re_path
from .views import (
    private_announcement_view,
    public_announcement_view,
    announcement_view,
)
from .consumers import AnnouncementConsumer

app_name = "announcements"

urlpatterns = [
    path("", announcement_view, name="announcement-view"),
    path("public", public_announcement_view, name="public-announcement-view"),
    path("private", private_announcement_view, name="private-announcement-view"),
]

ws_urlpatterns = [
    re_path(
        r"^ws/announcements/$",
        AnnouncementConsumer.as_asgi(),
    )
]
