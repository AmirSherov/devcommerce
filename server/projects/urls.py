from django.urls import path
from . import views
from . import comments_views

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
    
    # Лайк / дизлайк
    path('toggle-like/<uuid:project_id>/', views.toggle_project_like, name='toggle_project_like'),
    
    # Детали проекта
    path('<uuid:project_id>/', views.project_detail, name='project_detail'),
    path('recommended/<uuid:project_id>/', views.other_projects, name='other_projects'),

    # --- Комментарии к проектам ---
    path('<uuid:project_id>/comments/', comments_views.get_project_comments, name='get_project_comments'), # GET
    path('<uuid:project_id>/comments/create/', comments_views.create_project_comment, name='create_project_comment'), # POST
    path('comments/<int:comment_id>/edit/', comments_views.update_project_comment, name='update_project_comment'), # PATCH
    path('comments/<int:comment_id>/delete/', comments_views.delete_project_comment, name='delete_project_comment'), # DELETE
    path('comments/<int:comment_id>/like/', comments_views.like_project_comment, name='like_project_comment'), # POST
    path('comments/<int:comment_id>/pin/', comments_views.pin_project_comment, name='pin_project_comment'), # POST
] 