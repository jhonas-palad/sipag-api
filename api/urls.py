from django.urls import re_path, include

from django.conf import settings
from .views import index_view

app_name = "api"
urlpatterns = [
    re_path(r"^$", index_view, name="index-view"),
    re_path(r"^auth/", include("auth_api.urls", namespace="auth-api")),
    re_path(r"^users/", include("auth_api.users_urls", namespace="auth-api-users")),
]
