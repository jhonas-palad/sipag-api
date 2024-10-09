from django.urls import re_path, include, path
from .views import index_view, get_openai_token_view

app_name = "api"
urlpatterns = [
    path("openai/token", get_openai_token_view, name="get-openai-token-view"),
    re_path(r"^$", index_view, name="index-view"),
    re_path(r"^auth/", include("auth_api.urls", namespace="auth-api")),
    re_path(r"^users/", include("auth_api.users_urls", namespace="auth-api-users")),
    re_path(r"^waste-reports/", include("waste.urls", namespace="waste-report")),
    re_path(
        r"^announcements/", include("announcements.urls", namespace="announcements")
    ),
]
