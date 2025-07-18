# Generated by Django 5.2.3 on 2025-06-26 10:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolio', '0004_alter_portfolio_unique_together_alter_portfolio_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalAIStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Дата статистики', unique=True)),
                ('total_requests', models.IntegerField(default=0)),
                ('total_successful', models.IntegerField(default=0)),
                ('total_failed', models.IntegerField(default=0)),
                ('active_users', models.IntegerField(default=0, help_text='Активных пользователей')),
                ('new_users', models.IntegerField(default=0, help_text='Новых пользователей AI')),
                ('average_response_time', models.FloatField(default=0.0)),
                ('total_tokens_consumed', models.IntegerField(default=0)),
                ('total_cost', models.DecimalField(decimal_places=4, default=0, max_digits=12)),
                ('popular_styles', models.JSONField(default=dict)),
                ('popular_prompts', models.JSONField(default=list)),
                ('error_distribution', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Глобальная AI статистика',
                'verbose_name_plural': 'Глобальная AI статистика',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='AIGenerationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField(help_text='Промпт пользователя для AI')),
                ('title', models.CharField(help_text='Название проекта', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Описание проекта')),
                ('style', models.CharField(choices=[('modern', 'Современный'), ('minimal', 'Минимализм'), ('creative', 'Креативный'), ('business', 'Бизнес'), ('dark', 'Темная тема'), ('colorful', 'Яркий')], default='modern', max_length=50)),
                ('status', models.CharField(choices=[('processing', 'Обработка'), ('success', 'Успешно'), ('failed', 'Ошибка'), ('timeout', 'Таймаут'), ('ai_error', 'Ошибка AI'), ('invalid_response', 'Некорректный ответ AI')], default='processing', max_length=20)),
                ('response_time', models.FloatField(blank=True, help_text='Время ответа в секундах', null=True)),
                ('tokens_used', models.IntegerField(blank=True, help_text='Использовано токенов', null=True)),
                ('api_cost', models.DecimalField(blank=True, decimal_places=4, help_text='Стоимость запроса', max_digits=10, null=True)),
                ('error_message', models.TextField(blank=True, help_text='Сообщение об ошибке')),
                ('error_code', models.CharField(blank=True, help_text='Код ошибки', max_length=50)),
                ('ai_raw_response', models.TextField(blank=True, help_text='Сырой ответ от AI')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, help_text='Время начала обработки', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='Время завершения', null=True)),
                ('portfolio_created', models.ForeignKey(blank=True, help_text='Созданное портфолио (если успешно)', null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.portfolio')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AI запрос',
                'verbose_name_plural': 'AI запросы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIPromptTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название шаблона', max_length=100)),
                ('prompt', models.TextField(help_text='Текст промпта')),
                ('category', models.CharField(choices=[('landing', 'Лендинг'), ('portfolio', 'Портфолио'), ('blog', 'Блог'), ('ecommerce', 'Магазин'), ('corporate', 'Корпоративный'), ('creative', 'Креативный'), ('other', 'Другое')], default='other', max_length=20)),
                ('style', models.CharField(choices=[('modern', 'Современный'), ('minimal', 'Минимализм'), ('creative', 'Креативный'), ('business', 'Бизнес'), ('dark', 'Темная тема'), ('colorful', 'Яркий')], default='modern', max_length=50)),
                ('usage_count', models.IntegerField(default=0, help_text='Количество использований')),
                ('success_rate', models.FloatField(default=0.0, help_text='Процент успешных генераций')),
                ('is_public', models.BooleanField(default=False, help_text='Доступен другим пользователям')),
                ('is_featured', models.BooleanField(default=False, help_text='Рекомендуемый шаблон')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Шаблон промпта',
                'verbose_name_plural': 'Шаблоны промптов',
                'ordering': ['-usage_count', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIGenerationStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Дата статистики')),
                ('requests_count', models.IntegerField(default=0, help_text='Общее количество запросов')),
                ('successful_count', models.IntegerField(default=0, help_text='Успешных генераций')),
                ('failed_count', models.IntegerField(default=0, help_text='Неудачных генераций')),
                ('total_response_time', models.FloatField(default=0.0, help_text='Общее время ответов')),
                ('total_tokens_used', models.IntegerField(default=0, help_text='Общее количество токенов')),
                ('total_cost', models.DecimalField(decimal_places=4, default=0, help_text='Общая стоимость', max_digits=10)),
                ('popular_styles', models.JSONField(default=dict, help_text='Статистика по стилям')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_stats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Статистика AI',
                'verbose_name_plural': 'Статистика AI',
                'ordering': ['-date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
