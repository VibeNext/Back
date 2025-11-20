from rest_framework import serializers
from missions.serializers import MissionSerializer
from .models import SolutionHistory, Message

class SolutionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionHistory
        fields = "__all__"

class SolutionHistoryStatusUpdateSerializer(serializers.Serializer):
    is_solved = serializers.BooleanField()
    

class SolutionHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionHistory
        fields = ('id', 'created_at', 'is_solved', 'updated_at',)
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        return data
    
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['created_at', 'sender', 'content']
    
class SolutionHistoryDetailSerializer(serializers.Serializer):
    mission = MissionSerializer()
    messages = ChatMessageSerializer(many=True)
