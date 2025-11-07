from django.db.models import TextChoices, IntegerChoices

class MissionCategoryChoices(TextChoices):
    SEQUENCE   = 'sequence',   '순차'
    SELECTION  = 'selection',  '조건'
    REPETITION = 'repetition', '반복'
    
class Sender(IntegerChoices):
    USER = 0, '유저'
    AI = 1, 'AI'
