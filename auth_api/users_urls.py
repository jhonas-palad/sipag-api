from django.urls import re_path
from .views import upload_image_view

app_name = "auth_api_users"
urlpatterns = [re_path(r"^(?P<id>[0-9]+)/photo$", upload_image_view, name="user-photo")]
