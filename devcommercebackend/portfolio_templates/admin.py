from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils.safestring import mark_safe
from .models import PortfolioTemplate, TemplateUsage, TemplateLike


@admin.register(PortfolioTemplate)
class PortfolioTemplateAdmin(admin.ModelAdmin):
    """
    🎨 АДМИНКА ДЛЯ ШАБЛОНОВ ПОРТФОЛИО
    """
    
    list_display = [
        'title', 'category_display', 'difficulty', 'stats_display', 
        'status_display', 'is_active', 'is_featured', 'is_premium', 'created_at', 'actions_display'
    ]
    
    list_filter = [
        'category', 'difficulty', 'is_active', 'is_featured', 
        'is_premium', 'created_at'
    ]
    
    search_fields = [
        'title', 'description', 'tags', 'created_by__username'
    ]
    
    list_editable = ['is_active', 'is_featured', 'is_premium']
    
    readonly_fields = [
        'likes', 'views', 'uses', 'created_at', 'updated_at',
        'preview_display', 'code_preview'
    ]
    
    fieldsets = (
        ('📝 Основная информация', {
            'fields': (
                'title', 'description', 'category', 'difficulty',
                'created_by', 'tags'
            )
        }),
        ('🖼️ Превью и демо', {
            'fields': ('thumbnail_image', 'demo_url', 'preview_display'),
            'classes': ('collapse',)
        }),
        ('💻 Код шаблона', {
            'fields': ('html_code', 'css_code', 'js_code', 'code_preview'),
            'classes': ('collapse',)
        }),
        ('📊 Статистика', {
            'fields': ('likes', 'views', 'uses'),
            'classes': ('collapse',)
        }),
        ('⚙️ Настройки', {
            'fields': ('is_active', 'is_featured', 'is_premium')
        }),
        ('📅 Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def category_display(self, obj):
        """Отображение категории с иконкой"""
        category_icons = {
            'fullstack': '🌐',
            'frontend': '🎨',
            'backend': '⚙️',
            'mobile': '📱',
            'devops': '☁️',
            'data_scientist': '📊',
            'ml_engineer': '🤖',
            'qa_engineer': '🧪',
            'ui_designer': '🎭',
            'product_manager': '📋',
            'cyber_security': '🔒',
            'blockchain': '⛓️',
            'game_developer': '🎮',
            'ai_engineer': '🧠',
            'cloud_architect': '☁️',
            'business_analyst': '📈',
            'scrum_master': '🏃',
            'technical_writer': '📝',
            'sales_engineer': '💼',
            'other': '🔧'
        }
        
        icon = category_icons.get(obj.category, '🔧')
        return format_html(
            '{} {}',
            icon, obj.get_category_display()
        )
    category_display.short_description = "Категория"
    
    def stats_display(self, obj):
        """Отображение статистики"""
        return format_html(
            '<div style="font-size: 12px;">'
            '👁️ {} | 👍 {} | 🔥 {}'
            '</div>',
            obj.views, obj.likes, obj.uses
        )
    stats_display.short_description = "Статистика"
    
    def status_display(self, obj):
        """Отображение статуса"""
        status_parts = []
        
        if obj.is_featured:
            status_parts.append('<span style="color: #f39c12;">⭐ Топ</span>')
        
        if obj.is_premium:
            status_parts.append('<span style="color: #9b59b6;">💎 Premium</span>')
        
        if not obj.is_active:
            status_parts.append('<span style="color: #e74c3c;">❌ Неактивен</span>')
        elif obj.is_active:
            status_parts.append('<span style="color: #27ae60;">✅ Активен</span>')
        
        if obj.is_popular:
            status_parts.append('<span style="color: #e67e22;">🔥 Популярный</span>')
        
        return format_html('<br>'.join(status_parts))
    status_display.short_description = "Статус"
    
    def actions_display(self, obj):
        """Кнопки действий"""
        return format_html(
            '<a href="/admin/portfolio_templates/portfoliotemplate/{}/change/" '
            'style="background: #007cba; color: white; padding: 4px 8px; '
            'text-decoration: none; border-radius: 3px; font-size: 11px;">✏️ Редактировать</a>'
            '<br><br>'
            '<a href="#" onclick="window.open(\'/api/templates/{}/preview/\', \'_blank\')" '
            'style="background: #28a745; color: white; padding: 4px 8px; '
            'text-decoration: none; border-radius: 3px; font-size: 11px;">👁️ Превью</a>',
            obj.id, obj.id
        )
    actions_display.short_description = "Действия"
    
    def preview_display(self, obj):
        """Превью шаблона"""
        if obj.thumbnail_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; '
                'border: 1px solid #ddd; border-radius: 5px;" />',
                obj.thumbnail_image
            )
        return "Превью не загружено"
    preview_display.short_description = "Превью"
    
    def code_preview(self, obj):
        """Превью кода"""
        html_preview = obj.html_code[:200] + '...' if len(obj.html_code) > 200 else obj.html_code
        css_preview = obj.css_code[:200] + '...' if len(obj.css_code) > 200 else obj.css_code
        
        return format_html(
            '<div style="font-family: monospace; font-size: 12px;">'
            '<h4>HTML:</h4>'
            '<pre style="background: #f8f9fa; padding: 10px; overflow: auto; max-height: 150px;">{}</pre>'
            '<h4>CSS:</h4>'
            '<pre style="background: #f8f9fa; padding: 10px; overflow: auto; max-height: 150px;">{}</pre>'
            '</div>',
            html_preview, css_preview
        )
    code_preview.short_description = "Превью кода"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by').annotate(
            usage_count=Count('usages'),
            like_count=Count('template_likes')
        )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если создается новый объект
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TemplateUsage)
class TemplateUsageAdmin(admin.ModelAdmin):
    """
    📊 АДМИНКА ДЛЯ ИСПОЛЬЗОВАНИЙ ШАБЛОНОВ
    """
    
    list_display = [
        'template', 'user', 'portfolio_link', 'used_at'
    ]
    
    list_filter = ['used_at', 'template__category']
    
    search_fields = [
        'template__title', 'user__username', 'user__email'
    ]
    
    readonly_fields = ['used_at']
    
    def portfolio_link(self, obj):
        if obj.portfolio_created:
            return format_html(
                '<a href="/admin/portfolio/portfolio/{}/change/" target="_blank">'
                '📁 {}</a>',
                obj.portfolio_created.id,
                obj.portfolio_created.title
            )
        return "Портфолио не создано"
    portfolio_link.short_description = "Портфолио"


@admin.register(TemplateLike)
class TemplateLikeAdmin(admin.ModelAdmin):
    """
    👍 АДМИНКА ДЛЯ ЛАЙКОВ ШАБЛОНОВ
    """
    
    list_display = ['template', 'user', 'liked_at']
    list_filter = ['liked_at', 'template__category']
    search_fields = ['template__title', 'user__username']
    readonly_fields = ['liked_at']


# Кастомные действия для админки
@admin.action(description='🔥 Сделать рекомендуемыми')
def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)

@admin.action(description='⭐ Убрать из рекомендуемых')
def remove_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)

@admin.action(description='✅ Активировать шаблоны')
def activate_templates(modeladmin, request, queryset):
    queryset.update(is_active=True)

@admin.action(description='❌ Деактивировать шаблоны')
def deactivate_templates(modeladmin, request, queryset):
    queryset.update(is_active=False)

# Добавляем действия к админке
PortfolioTemplateAdmin.actions = [
    make_featured, remove_featured, 
    activate_templates, deactivate_templates
]
