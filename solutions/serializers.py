from rest_framework import serializers
from .models import SolutionHistory, Message
from django.urls import reverse
from missions.serializers import MissionSerializer

class SolutionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionHistory
        fields = "__all__"

class SolutionHistoryStatusUpdateSerializer(serializers.Serializer):
    is_solved = serializers.BooleanField()
    

class SolutionHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionHistory
        fields = ['id', 'created_at', 'is_solved', 'updated_at']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # is_solved가 False면 updated_at 키 제거
        if not data.get("is_solved"):
            data.pop("updated_at", None)

        return data
    
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['created_at', 'sender', 'content']
    
class SolutionHistoryDetailSerializer(serializers.Serializer):
    mission = MissionSerializer()
    messages = ChatMessageSerializer(many=True)
