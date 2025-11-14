import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from missions.models import Badge, Chapter, Mission

class Command(BaseCommand):
    help = 'Insert data'
    MODEL_MAP = {
        # 문자열: 모델
        'Badge': Badge,
        'Chapter': Chapter,
        'Mission': Mission,
    }
    FK_MAP = {
        # 모델: 외래키 필드 모델 튜플
        Chapter: (Badge,),
        Mission: (Chapter,)
    }

    def _get_model(self, model_name:str):
        model = self.MODEL_MAP.get(model_name)
        if not model:
            raise CommandError('모델 이름이 올바르지 않습니다.')
        return model

    def _get_instance(self, model, data_item):
        if model in self.FK_MAP:
            for fk_model in self.FK_MAP[model]:
                fk_field_name = fk_model.__name__.lower()
                fk_id = data_item.pop(fk_field_name)
                fk_instance = fk_model.objects.get(id=fk_id) if fk_id else None
                data_item[fk_field_name] = fk_instance
        return model(**data_item)

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

        instances = model.objects.bulk_create([
            self._get_instance(model, data_item)
            for data_item in data_list
        ])

        self.stdout.write(self.style.SUCCESS(f'{model_name} 데이터 {len(instances)}개를 추가했습니다.'))
