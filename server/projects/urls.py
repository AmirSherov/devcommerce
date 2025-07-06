from django.urls import path
from . import views

urlpatterns = [
    # Публичные проекты
    path('', views.project_list, name='project_list'),
    
    # Проекты пользователя
    path('me/', views.my_projects, name='my_projects'),
    path('user/<str:username>/', views.user_projects, name='user_projects'),
    
    # Управление проектами
    path('create/me/', views.create_project, name='create_project'),
    path('me/<uuid:project_id>/', views.update_project, name='update_project'),
    path('delete/me/<uuid:project_id>/', views.delete_project, name='delete_project'),
    path('status/me/<uuid:project_id>/', views.update_project_status, name='update_project_status'),
    
    # Детали проекта
    path('<str:slug>/', views.project_detail, name='project_detail'),
] 