from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import time


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


index_view = IndexView.as_view()
