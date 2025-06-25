from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_list, name='portfolio_list'),
    path('me/', views.my_portfolios, name='my_portfolios'),
    path('create/', views.create_portfolio, name='create_portfolio'),
    path('<uuid:portfolio_id>/', views.portfolio_detail, name='portfolio_detail'),
    path('<uuid:portfolio_id>/update/', views.update_portfolio, name='update_portfolio'),
    path('<uuid:portfolio_id>/autosave/', views.autosave_portfolio, name='autosave_portfolio'),
    path('<uuid:portfolio_id>/delete/', views.delete_portfolio, name='delete_portfolio'),
    path('<uuid:portfolio_id>/like/', views.toggle_portfolio_like, name='toggle_portfolio_like'),
    path('user/<str:username>/', views.user_portfolios, name='user_portfolios'),
    path('stats/me/', views.my_portfolio_stats, name='my_portfolio_stats'),
    path('stats/global/', views.portfolio_stats, name='portfolio_stats'),
    path('slug/<str:slug>/', views.get_portfolio_by_slug, name='get_portfolio_by_slug'),
    path('<uuid:portfolio_id>/view/', views.record_portfolio_view_api, name='record_portfolio_view_api'),
] 