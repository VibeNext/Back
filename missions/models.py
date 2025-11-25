from django.db import models

class Badge(models.Model):
    id = models.IntegerField(
        primary_key=True,
        editable=False,
    )
    name = models.CharField(
        max_length=12,
    )
    description = models.CharField(
        max_length=35,
    )
    image = models.URLField()

    def __str__(self):
        return self.name

class Chapter(models.Model):
    id = models.IntegerField(
        primary_key=True,
        editable=False,
    )
    title = models.CharField(
        max_length=2,
    )
    subtitle = models.CharField(
        max_length=10,
    )
    badge = models.OneToOneField(
        'Badge',
        on_delete=models.RESTRICT,
        related_name='chapter',
    )

class Mission(models.Model):
    id = models.IntegerField(
        primary_key=True,
        editable=False,
    )
    chapter = models.ForeignKey(
        'Chapter',
        on_delete=models.CASCADE,
        related_name='mission',
    )
    title = models.CharField(
        max_length=25,
    )
    description = models.CharField(
        max_length=50,
    )
    image = models.URLField()
    question_text = models.TextField()
    question_hint = models.TextField()
    question_image = models.URLField()
    answer_assets = models.JSONField(
        default=dict,
    )
    ai_prompt = models.TextField()

    def __str__(self):
        return self.title
