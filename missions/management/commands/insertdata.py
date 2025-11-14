import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from missions.models import Badge, Chapter, Mission

class Command(BaseCommand):
    help = 'Insert data'

    def _get_model(self, model_name:str):
        if(model_name == 'Badge'):
            return Badge
        elif(model_name == 'Chapter'):
            return Chapter
        elif(model_name == 'Mission'):
            return Mission
        else:
            raise CommandError('모델 이름이 올바르지 않습니다.')

    def _get_instance(self, model, data_item):
        if(model == Badge):
            return Badge(**data_item)
        elif(model == Chapter):
            badge_id = data_item.pop('badge', None)
            badge = Badge.objects.get(id=badge_id) if badge_id else None
            return Chapter(badge=badge, **data_item)
        elif(model == Mission):
            chapter_id = data_item.pop('chapter', None)
            chapter = Chapter.objects.get(id=chapter_id) if chapter_id else None
            return Mission(chapter=chapter, **data_item)

    def add_arguments(self, parser):
        parser.add_argument('-m', '--model', required=True, type=str)

    def handle(self, *args, **options):
        model_name = options['model'].capitalize()
        model = self._get_model(model_name)

        with open(
            file=os.path.join(settings.BASE_DIR, 'missions', 'datas', f'{model_name.lower()}.json'),
            mode='r',
            encoding='utf-8'
        ) as file:
            data_list = json.load(file)

        instance_list = list()
        for data_item in data_list:
            instance = self._get_instance(model, data_item)
            instance_list.append(instance)

        instances = model.objects.bulk_create(instance_list)

        self.stdout.write(self.style.SUCCESS(f'{model_name} 데이터 {len(instances)}개를 추가했습니다.'))
