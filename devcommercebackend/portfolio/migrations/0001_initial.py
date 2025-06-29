# Generated by Django 5.2.3 on 2025-06-24 09:33

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('html_file_key', models.CharField(blank=True, max_length=500)),
                ('css_file_key', models.CharField(blank=True, max_length=500)),
                ('js_file_key', models.CharField(blank=True, max_length=500)),
                ('html_content', models.TextField(default='<!DOCTYPE html>\n<html lang="ru">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Мой проект</title>\n    <link rel="stylesheet" href="style.css">\n</head>\n<body>\n    <h1>Привет, мир!</h1>\n    <p>Это мой первый проект портфолио.</p>\n    <script src="script.js"></script>\n</body>\n</html>')),
                ('css_content', models.TextField(default='/* Ваши CSS стили */\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n    background-color: #f5f5f5;\n}\n\nh1 {\n    color: #333;\n    text-align: center;\n}\n\np {\n    color: #666;\n    line-height: 1.6;\n}')),
                ('js_content', models.TextField(default='// Ваш JavaScript код\nconsole.log("Привет из портфолио!");\n\n// Пример интерактивности\ndocument.addEventListener("DOMContentLoaded", function() {\n    const h1 = document.querySelector("h1");\n    if (h1) {\n        h1.addEventListener("click", function() {\n            alert("Вы кликнули на заголовок!");\n        });\n    }\n});')),
                ('is_public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('likes', models.PositiveIntegerField(default=0)),
                ('tags', models.JSONField(blank=True, default=list)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolios', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
                'unique_together': {('author', 'slug')},
            },
        ),
        migrations.CreateModel(
            name='PortfolioLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_likes', to='portfolio.portfolio')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('portfolio', 'user')},
            },
        ),
        migrations.CreateModel(
            name='PortfolioView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_views', to='portfolio.portfolio')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('portfolio', 'ip_address')},
            },
        ),
    ]
