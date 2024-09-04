from django.urls import re_path
from .consumers import WasteReportActivityNotificationConsumer
from .views import (
    waste_report_view,
    waste_report_task_view,
    waste_report_activities_view,
)

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
    re_path(
        r"^activites$",
        waste_report_activities_view,
        name="waste-report-task-view",
    ),
]


ws_urlpatterns = [
    re_path(
        r"^waste-report-activities/$", WasteReportActivityNotificationConsumer.as_asgi()
    )
]
