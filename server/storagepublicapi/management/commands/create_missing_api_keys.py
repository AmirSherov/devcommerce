from django.core.management.base import BaseCommand
from storage.models import StorageContainer
from storagepublicapi.models import PublicAPIKey
import logging
from django.db.models import Q
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Создает PublicAPIKey для всех контейнеров, у которых их нет'

    def handle(self, *args, **options):
        containers_without_keys = StorageContainer.objects.filter(
            is_active=True
        ).exclude(
            public_api_key__isnull=False
        )
        
        created_count = 0
        for container in containers_without_keys:
            try:
                PublicAPIKey.objects.create(
                    container=container,
                    permissions={},
                    rate_limit_per_hour=1000,
                    max_file_size_mb=100
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Создан PublicAPIKey для контейнера "{container.name}"')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка создания PublicAPIKey для контейнера "{container.name}": {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Создано {created_count} PublicAPIKey для существующих контейнеров')
        ) 