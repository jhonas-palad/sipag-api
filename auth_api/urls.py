from django.urls import re_path, path
from .views import login_view, signup_view, signout_view
from rest_framework_simplejwt.views import TokenVerifyView

app_name = "auth_api"

urlpatterns = [
    re_path(r"^signin$", login_view, name="login-view"),
    re_path(r"^signup$", signup_view, name="signup-view"),
    re_path(r"^signout$", signout_view, name="signout-view"),
    re_path(r"^verify$", TokenVerifyView.as_view(), name="token_verify"),
    
]
