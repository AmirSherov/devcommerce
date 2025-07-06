from django.urls import path
from . import views

app_name = 'portfolio_templates'

urlpatterns = [
    path('', views.PortfolioTemplateListView.as_view(), name='template_list'),
    path('<int:template_id>/', views.PortfolioTemplateDetailView.as_view(), name='template_detail'),
    path('<int:template_id>/preview/', views.PortfolioTemplatePreviewView.as_view(), name='template_preview'),
    path('use/', views.UseTemplateView.as_view(), name='use_template'),
    path('<int:template_id>/like/', views.TemplateLikeView.as_view(), name='template_like'),
    path('stats/', views.TemplateStatsView.as_view(), name='template_stats'),
    path('categories/', views.template_categories_view, name='template_categories'),
] 