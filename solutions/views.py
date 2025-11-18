# app/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import SolutionHistory, Message
from .serializers import SolutionHistoryListSerializer, SolutionHistoryDetailSerializer


class SolutionHistoryListView(generics.ListAPIView):
    serializer_class = SolutionHistoryListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        mission_id = self.kwargs.get("mission_id")
        user = self.request.user

        return (
            SolutionHistory.objects
            .filter(user=user, mission_id=mission_id)
            .order_by("created_at")
        )

class SolutionHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = SolutionHistoryDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, solution_history_id):
        # 1) 풀이기록 조회
        solution_history = get_object_or_404(SolutionHistory, pk=solution_history_id)

        # 2) 메시지 조회 (해당 풀이기록 FK + 오래된 것부터)
        messages = Message.objects.filter(
            solution_history=solution_history
        ).order_by("created_at")

        # 3) 풀이기록이 어떤 mission인지
        mission = solution_history.mission  # FK라고 가정

        # 4) serializer에 묶어서 넣기
        serializer = SolutionHistoryDetailSerializer({
            "mission": mission,
            "messages": messages,
        })

        return Response(serializer.data)