
from rest_framework import generics, status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from missions.models import Mission

from .models import SolutionHistory, Message
from .serializers import SolutionHistoryListSerializer, SolutionHistoryDetailSerializer, SolutionHistorySerializer, SolutionHistoryStatusUpdateSerializer


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

    def get(self, solution_history_id):
        solution_history = get_object_or_404(SolutionHistory, pk=solution_history_id)
        messages = Message.objects.filter(
            solution_history=solution_history
        ).order_by("created_at")

        mission = solution_history.mission 

        serializer = SolutionHistoryDetailSerializer({
            "mission": mission,
            "messages": messages,
        })

        return Response(serializer.data)
    
    

class SolutionHistoryCreateView(generics.CreateAPIView):
    queryset = SolutionHistory.objects.all()
    serializer_class = SolutionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]  # 로그인

    def perform_create(self, serializer):
        mission_id = self.kwargs["mission_id"]  # path param
        mission = get_object_or_404(Mission, pk=mission_id)

        serializer.save(
            user=self.request.user,
            mission=mission,
        )
        
class SolutionHistoryUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        # 요청 바디 검증
        serializer = SolutionHistoryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        solution_history_id = data["solution_history_id"]
        is_solved = data["is_solved"]
        updated_at = data["updated_at"]

        instance = get_object_or_404(
            SolutionHistory,
            pk=solution_history_id,
            user=request.user,  
        )

        instance.is_solved = is_solved
        instance.save()

        try:
            from .serializers import SolutionHistorySerializer
            response_data = SolutionHistorySerializer(instance).data
        except ImportError:
            # 간단하게만
            response_data = {
                "solution_history_id": solution_history_id,
                "is_solved": is_solved,
                "updated_at": instance.updated_at,
            }

        return Response(response_data, status=status.HTTP_200_OK)