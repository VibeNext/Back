import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from missions.models import Badge, Mission

class Command(BaseCommand):
    help = 'Insert mission data'

    def handle(self, *args, **options):
        with open(
            file=os.path.join(settings.BASE_DIR, 'missions', 'datas', 'mission.json'),
            mode='r',
            encoding='utf-8'
        ) as file:
            data_list = json.load(file)

        mission_list = list()
        for data_item in data_list:
            badge_id = data_item.pop('badge', None)
            badge = Badge.objects.get(id=badge_id) if badge_id else None

            mission = Mission(
                badge=badge,
                **data_item
            )
            mission_list.append(mission)

        missions = Mission.objects.bulk_create(mission_list)

        self.stdout.write(self.style.SUCCESS(f'Mission 데이터 {len(missions)}개를 추가했습니다.'))
