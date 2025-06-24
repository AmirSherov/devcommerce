from django.contrib import admin
from django.utils.html import format_html
from .models import Portfolio, PortfolioLike, PortfolioView


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'is_public', 'views', 'likes', 
        'created_at', 'updated_at', 'preview_link'
    ]
    list_filter = ['is_public', 'created_at', 'updated_at', 'tags']
    search_fields = ['title', 'description', 'author__username', 'author__email']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at', 'views', 'likes', 'preview_link']
    filter_horizontal = []
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'author', 'slug', 'is_public', 'tags')
        }),
        ('Код проекта', {
            'fields': ('html_content', 'css_content', 'js_content'),
            'classes': ('collapse',)
        }),
        ('S3 файлы', {
            'fields': ('html_file_key', 'css_file_key', 'js_file_key'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('views', 'likes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Ссылки', {
            'fields': ('preview_link',),
            'classes': ('collapse',)
        }),
    )
    
    def preview_link(self, obj):
        if obj.public_url:
            return format_html(
                '<a href="{}" target="_blank">Открыть превью</a>',
                obj.public_url
            )
        return "Нет ссылки"
    preview_link.short_description = "Превью"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')


@admin.register(PortfolioLike)
class PortfolioLikeAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['portfolio__title', 'user__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('portfolio', 'user')


@admin.register(PortfolioView)
class PortfolioViewAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['portfolio__title', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('portfolio', 'user')
