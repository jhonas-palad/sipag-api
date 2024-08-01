from rest_framework.serializers import ModelSerializer
from .models import WasteReport, WasteReportActivity

class WasteReportSerializer(ModelSerializer):
    
    class Meta:
        model = WasteReport
        fields = [
            "id",
            "status",
            "description",
            
        ]