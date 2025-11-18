from django.urls import path
from .views import *

app_name = 'solutions'

urlpatterns = [
    path('list/<int:pk>/', SolutionHistoryListView.as_view(), name='solution-list'),
    path('detail/<int:pk>/', SolutionHistoryDetailView.as_view(), name='solution-detail'),
    
]