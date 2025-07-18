"""
URL configuration for devcommercebackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from portfolio.views import public_portfolio_site

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/ai/', include('ai_generator.urls')),
    path('api/templates/', include('portfolio_templates.urls')),
    path('api/storage/', include('storage.urls')),
    path('api/remote/storage/', include('storagepublicapi.urls')),
    path('site/<uuid:portfolio_id>/', public_portfolio_site, name='public_portfolio_site'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
