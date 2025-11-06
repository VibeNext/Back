from django.db.models import TextChoices, IntegerChoices

class Sender(IntegerChoices):
    USER = 0, '유저'
    AI = 1, 'AI'