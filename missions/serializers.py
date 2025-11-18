from rest_framework import serializers
from .models import Chapter, Mission

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = [
            "id",
            "chapter",
            "title",
            "description",
            "image",
            "question_text",
            "question_image",
            "answer_assets",
            "ai_prompt",
        ]

class ChapterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ('id','title','subtitle',)

class MissionListSerializer(serializers.ModelSerializer):
    number = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = ('id','chapter','number','title','description','image',)

    def get_number(self, obj):
        return obj.id % 10
