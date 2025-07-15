from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    # Контейнеры
    path('containers/', views.StorageContainerView.as_view(), name='containers'),
    path('containers/<uuid:container_id>/', views.StorageContainerDetailView.as_view(), name='container_detail'),
    path('containers/<uuid:container_id>/stats/', views.ContainerStatsView.as_view(), name='container_stats'),
    path('containers/<uuid:container_id>/logs/', views.ContainerApiLogsView.as_view(), name='container_logs'),
    
    # Файлы
    path('containers/<uuid:container_id>/upload/', views.StorageFileUploadView.as_view(), name='file_upload'),
    path('containers/<uuid:container_id>/files/', views.StorageFileListView.as_view(), name='file_list'),
    path('files/<uuid:file_id>/', views.StorageFileDetailView.as_view(), name='file_detail'),
    
    # Лимиты и статистика
    path('limits/', views.StorageLimitsView.as_view(), name='limits'),
    path('stats/', views.StorageStatsView.as_view(), name='stats'),
] 