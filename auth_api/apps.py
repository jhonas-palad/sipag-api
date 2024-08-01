from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_api"

    def ready(self) -> None:
        from django.views import defaults
        from rest_framework.response import Response
        from rest_framework.generics import GenericAPIView
        from rest_framework import status

        class Handle404VIew(GenericAPIView):
            def get(self, request, *args, **kwargs):
                return Response(
                    {"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND
                )

        defaults.page_not_found = Handle404VIew.as_view()
        return super().ready()
