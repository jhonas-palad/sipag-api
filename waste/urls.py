from django.urls import re_path
from .views import waste_report_view

app_name = "waste"

urlpatterns = [re_path(r"^(?P<id>\d+)?$", waste_report_view, name="waste")]
