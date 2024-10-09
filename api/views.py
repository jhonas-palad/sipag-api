from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
import time
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings


class IndexView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response(
            data={
                "status": "success",
                "message": "Successful",
                "version": request.version,
            }
        )


class GetOpenAITokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = settings.OPENAI_TOKEN
        return Response(data={"token": token}, status=status.HTTP_200_OK)


get_openai_token_view = GetOpenAITokenView.as_view()

index_view = IndexView.as_view()
