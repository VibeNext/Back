from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from missions.models import Mission
from .models import SolutionHistory, Message
from .serializers import (
    SolutionHistoryListSerializer,
    SolutionHistoryDetailSerializer,
    SolutionHistorySerializer,
)
from .services import validate_allowed_fields


class SolutionHistoryListCreateView(generics.ListCreateAPIView):
    
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SolutionHistoryListSerializer
        return SolutionHistorySerializer

    def get_queryset(self):
        mission_id = self.kwargs.get("mission_id")
        user = self.request.user

        return (
            SolutionHistory.objects
            .filter(user=user, mission_id=mission_id)
            .order_by("created_at")
        )

    def perform_create(self, serializer):
        mission_id = self.kwargs.get("mission_id")
        mission = get_object_or_404(Mission, pk=mission_id)

        # read_only field
        serializer.save(
            user=self.request.user,
            mission=mission,
        )


class SolutionHistoryUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, solution_history_id):
        validate_allowed_fields(request.data, {"is_solved"})

        instance = get_object_or_404(
            SolutionHistory,
            pk=solution_history_id,
            user=request.user,
        )

        serializer = SolutionHistorySerializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

class SolutionHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solution_history_id):
        solution_history = get_object_or_404(
            SolutionHistory,
            pk=solution_history_id,
            user=request.user,  
        )

        messages = Message.objects.filter(
            solution_history=solution_history
        ).order_by("created_at")

        mission = solution_history.mission

        serializer = SolutionHistoryDetailSerializer(
            {
                "mission": mission,
                "messages": messages,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
