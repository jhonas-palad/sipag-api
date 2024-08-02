from django.urls import re_path
from .views import login_view, signup_view, upload_image_view


app_name = "auth_api"

urlpatterns = [
    re_path(r"^signin$", login_view, name="login-view"),
    re_path(r"^signup$", signup_view, name="signup-view"),
]
