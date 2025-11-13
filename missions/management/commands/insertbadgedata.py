import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from missions.models import Badge

class Command(BaseCommand):
    help = 'Insert badge data'

    def handle(self, *args, **options):
        with open(
            file=os.path.join(settings.BASE_DIR, 'missions', 'datas', 'badge.json'),
            mode='r',
            encoding='utf-8'
        ) as file:
            data_list = json.load(file)

        badge_list = list()
        for data_item in data_list:
            badge = Badge(**data_item)
            badge_list.append(badge)

        badges = Badge.objects.bulk_create(badge_list)

        self.stdout.write(self.style.SUCCESS(f'Badge 데이터 {len(badges)}개를 추가했습니다.'))
