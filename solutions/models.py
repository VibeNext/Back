from django.db import models

# Create your models here.

class SolutionHistory(models.Model):
    user=models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    mission=models.ForeignKey('missions.Mission', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    solved_at = models.DateTimeField(null=True, blank=True)
    is_solved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Sender(models.TextChoices):
    USER = 'user', 'User'
    AI = 'ai', 'AI'


    
class Message(models.Model):
    solution_history = models.ForeignKey(SolutionHistory, on_delete=models.CASCADE, related_name='messages')
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(
        max_length=10,
        choices=Sender.choices,
        default=Sender.USER
    )
    content = models.TextField()
    

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"