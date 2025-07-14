from django.urls import path
from . import views

app_name = 'storagepublicapi'

urlpatterns = [
    # API ключи
    path('keys/', views.PublicAPIKeyView.as_view(), name='api_keys'),
    path('upload/', views.PublicFileUploadView.as_view(), name='file_upload'),
    path('files/', views.PublicFileListView.as_view(), name='file_list'),
    path('files/<uuid:file_id>/', views.PublicFileDetailView.as_view(), name='file_detail'),
    path('stats/', views.PublicAPIStatsView.as_view(), name='api_stats'),
] 