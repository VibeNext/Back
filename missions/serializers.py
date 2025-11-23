from rest_framework import serializers
from .models import Chapter, Mission

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ("id","chapter","title","question_text","question_image","answer_assets",)

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

class MissionListLoginSerializer(MissionListSerializer):
    is_unlocked = serializers.BooleanField()

    class Meta(MissionListSerializer.Meta):
        fields = MissionListSerializer.Meta.fields + ('is_unlocked',)
