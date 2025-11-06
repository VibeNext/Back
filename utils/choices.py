from django.db.models import TextChoices, IntegerChoices

class MissionCategoryChoices(TextChoices):
    SEQUENCE   = 'sequence',   '순차'
    SELECTION  = 'selection',  '조건'
    REPETITION = 'repetition', '반복'
