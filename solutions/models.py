from django.db import models
from django_nanoid.models import NanoIDField 
from utils.choices import Sender

# Create your models here.

class SolutionHistory(models.Model):
    id = NanoIDField(
    primary_key=True,
    editable=False,
    unique=True,
    max_length=21,
    )
    user=models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='solutionhistory')
    mission=models.ForeignKey('missions.Mission', on_delete=models.CASCADE, related_name='solutionhistory')
    created_at = models.DateTimeField(auto_now_add=True)
    solved_at = models.DateTimeField(null=True, blank=True)
    is_solved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} {self.mission.title} {self.created_at}"


    
class Message(models.Model):
    solution_history = models.ForeignKey(SolutionHistory, on_delete=models.CASCADE, related_name='message')
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(
        max_length=10,
        choices=Sender.choices,
        default=Sender.USER
    )
    content = models.TextField()
    

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"