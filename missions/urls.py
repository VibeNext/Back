from django.urls import path
from .views import *

app_name = 'missions'

urlpatterns = [
    path('', Root.as_view()),
]
