from django.contrib.postgres.fields import ArrayField
from django.db import models
from utils.choices import MissionCategoryChoices

class Badge(models.Model):
    id = models.CharField(
        primary_key=True,
        editable=False,
        max_length=10,
    )
    name = models.CharField(
        max_length=12,
    )
    description = models.CharField(
        max_length=35,
    )
    image = models.ImageField(
        upload_to='badge/image',
    )

class Mission(models.Model):
    id = models.IntegerField(
        primary_key=True,
        editable=False,
    )
    badge = models.OneToOneField(
        'Badge',
        on_delete=models.RESTRICT,
        related_name='mission',
        null=True,
        blank=True,
    )
    category = models.CharField(
        max_length=10,
        choices=MissionCategoryChoices.choices,
    )
    title = models.CharField(
        max_length=25,
    )
    question_text = models.TextField()
    question_image = models.ImageField(
        upload_to='mission/question_image',
    )
    ai_prompt = models.TextField()
    answer_assets = ArrayField(
        base_field=models.JSONField(
            default=dict,
        ),
        size=None,
    )
