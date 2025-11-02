from django.db import models

# Create your models here.

class SolutionHistory(models.Model):
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE)
    mission=models.ForeignKey('missions.Mission', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    solved_at = models.DateTimeField(null=True, blank=True)
    is_solved = models.BooleanField(default=False)

    def __str__(self):
        return self.title