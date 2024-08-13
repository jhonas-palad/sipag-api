from django.urls import re_path
from .views import waste_report_view, waste_report_task_view

app_name = "waste"

urlpatterns = [
    re_path(r"^(?P<pk>\d+)?$", waste_report_view, name="waste"),
    # re_path(
    #     r"^tasks$",
    #     waste_report_view_task,
    #     name="waste-report-view-task",
    # ),
    re_path(
        r"^(?P<post_id>\d+)/tasks$",
        waste_report_task_view,
        name="waste-report-task-view",
    ),
]
