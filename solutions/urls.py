from django.urls import path
from .views import *

app_name = 'solutions'

urlpatterns = [

    path('<int:mission_id>/', SolutionHistoryListCreateView.as_view(), name='solution-list-and-create'),
    path('detail/<str:solution_history_id>/', SolutionHistoryDetailView.as_view(), name='solution-detail'),
    path("update/<str:solution_history_id>/", SolutionHistoryUpdateView.as_view(), name="solution-update"),
]
