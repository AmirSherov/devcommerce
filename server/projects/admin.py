from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'likes', 'views', 'created_at')
    list_filter = ('status', 'created_at', 'technologies')
    search_fields = ('title', 'description', 'author__username', 'author__email')
    readonly_fields = ('id', 'slug', 'likes', 'views', 'comments_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'author', 'slug')
        }),
        ('Ссылки', {
            'fields': ('github_link', 'project_public_link', 'project_photo')
        }),
        ('Настройки', {
            'fields': ('status', 'technologies')
        }),
        ('Статистика', {
            'fields': ('likes', 'views', 'comments_count'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)
