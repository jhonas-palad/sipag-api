from django.urls import re_path
from .views import index_view
app_name = 'api'
urlpatterns = [
   re_path(r'^$', index_view, name='index-view') 
]