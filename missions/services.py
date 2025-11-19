from django.http import HttpRequest
from .models import Chapter, Mission
from .serializers import ChapterListSerializer, MissionListSerializer

class ChapterService:
    def __init__(self, request:HttpRequest):
        self.request = request

    def get_list(self):
        chapters = Chapter.objects.all().order_by('id')
        chapter_list_serializer = ChapterListSerializer(chapters, many=True)
        return chapter_list_serializer.data

class MissionService:
    def __init__(self, request:HttpRequest):
        self.request = request

    def get_list(self):
        missions = Mission.objects.all().order_by('id')
        mission_list_serializer = MissionListSerializer(missions, many=True)
        return mission_list_serializer.data
