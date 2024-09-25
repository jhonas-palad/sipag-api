from django.urls import re_path
from .consumers import WasteReportActivityNotificationConsumer
from .views import (
    waste_report_view,
    waste_report_task_view,
    waste_report_activities_view,
    cleaner_retrieve_view,
    redeem_record_view,
)

app_name = "waste"

urlpatterns = [
    re_path(
        r"^cleaner-details/(?P<pk>\d+)$",
        cleaner_retrieve_view,
        name="cleaner-retrieve-view",
    ),
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
    re_path(r"^redeem-records$", redeem_record_view, name="redeem-records-view"),
]


ws_urlpatterns = [
    re_path(
        r"^ws/waste-report-activities/$",
        WasteReportActivityNotificationConsumer.as_asgi(),
    )
]
