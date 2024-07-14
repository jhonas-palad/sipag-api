from rest_framework.views import APIView
from rest_framework.response import Response

class IndexView(APIView):
    def get(self, request):
        return Response(
            data = {
                'status': 'success',
                'message': 'Successful',
                'version': request.version
            }
        )

index_view = IndexView.as_view()