
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
        
class SolutionHistoryDetailView(APIView):
    serializer_class = SolutionHistoryDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        solution_history_id = kwargs.get("solution_history_id")

        solution_history = get_object_or_404(
            SolutionHistory,
            pk=solution_history_id,
        )

        messages = Message.objects.filter(
            solution_history=solution_history
        ).order_by("created_at")

        mission = solution_history.mission

        serializer = SolutionHistoryDetailSerializer({
            "mission": mission,
            "messages": messages,
        })

        return Response(serializer.data)

    
class SolutionHistoryCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        mission_id = request.data.get("mission_id")
        if mission_id is None:
            return Response(
                {"mission_id": ["이 필드는 필수 항목입니다."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mission = get_object_or_404(Mission, pk=mission_id)

        solution = SolutionHistory.objects.create(
            user=request.user,
            mission=mission,
        )

        return Response(
            SolutionHistorySerializer(solution).data,
            status=status.HTTP_201_CREATED,
        )
        
class SolutionHistoryUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, solution_history_id):
        
        serializer = SolutionHistoryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_solved = serializer.validated_data["is_solved"]

        instance = get_object_or_404(
            SolutionHistory,
            pk=solution_history_id,
        )

        instance.is_solved = is_solved
        instance.save()   # updated_at 자동 업데이트

        response = SolutionHistorySerializer(instance)
        return Response(response.data, status=status.HTTP_200_OK)
