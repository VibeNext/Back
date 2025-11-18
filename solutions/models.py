from django.db import models
from django_nanoid.models import NANOIDField 
from utils.choices import Sender

# Create your models here.

class SolutionHistory(models.Model):
    id = NANOIDField(
    primary_key=True,   
    editable=False,
    unique=True,
    max_length=21,
    )
    user=models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='solution_history')
    mission=models.ForeignKey('missions.Mission', on_delete=models.CASCADE, related_name='solution_history')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    is_solved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} {self.mission.title} {self.created_at}"


    
class Message(models.Model):
    solution_history = models.ForeignKey(SolutionHistory, on_delete=models.CASCADE, related_name='message')
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.IntegerField(
        choices=Sender.choices,
    )
    content = models.TextField()
    

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"