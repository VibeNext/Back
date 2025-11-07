from django.contrib import admin

# Register your models here.
from .models import SolutionHistory, Message

admin.site.register(SolutionHistory)
admin.site.register(Message)
