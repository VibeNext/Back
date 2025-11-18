from django.urls import path
from .views import *

app_name = 'solutions'

urlpatterns = [
    path('list/<int:mission_id>/', SolutionHistoryListView.as_view(), name='solution-list'),
    path('detail/<str:solution_history_id>/', SolutionHistoryDetailView.as_view(), name='solution-detail'),
    path("new/", SolutionHistoryCreateView.as_view(), name="solution-create"),
    path("update/<str:solution_history_id>/", SolutionHistoryUpdateView.as_view(), name="solution-update"),
]