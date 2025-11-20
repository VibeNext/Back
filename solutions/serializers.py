from rest_framework import serializers
from missions.serializers import MissionSerializer
from .models import SolutionHistory, Message


class SolutionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionHistory
        fields = "__all__"
        read_only_fields = ("id", "user", "mission", "created_at", "updated_at")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and not validated_data.get("user"):
            validated_data["user"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        
        is_solved = validated_data.get("is_solved", instance.is_solved)
        instance.is_solved = is_solved
        instance.save()
        return instance
    


class SolutionHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionHistory
        fields = ("id", "created_at", "is_solved", "updated_at")

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("created_at", "sender", "content")


class SolutionHistoryDetailSerializer(serializers.Serializer):
    mission = MissionSerializer()
    messages = ChatMessageSerializer(many=True)
