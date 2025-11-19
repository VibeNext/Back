from django.db.models import Case, Exists, F, OuterRef, Q, Value, When, BooleanField, IntegerField
from django.db.models.functions import Floor, Mod
from django.http import HttpRequest
from solutions.models import SolutionHistory
from .models import Chapter, Mission
from .serializers import ChapterListSerializer, MissionListSerializer, MissionListLoginSerializer

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

    def get_list_login(self):
        missions = Mission.objects.annotate(
            id_mod_10=Mod(F('id'), 10),
        )

        prev_mission_id = Case(
            When(id=11, then=Value(None)),
            When(~Q(id_mod_10=1), then=F('id')-1),
            When(id_mod_10=1, then=Floor(F('id')/10)*10-10+3),
            output_field=IntegerField(),
        )

        prev_mission_is_solved = Exists(
            SolutionHistory.objects.filter(
                mission_id=OuterRef('prev_mission_id'),
                user=self.request.user,
                is_solved=True,
            )
        )

        missions = missions.annotate(
            prev_mission_id=prev_mission_id,
            is_unlocked=Case(
                When(prev_mission_id__isnull=True, then=Value(True)),
                When(prev_mission_is_solved, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        ).all(
        ).order_by('id')

        mission_list_serializer = MissionListLoginSerializer(missions, many=True)
        return mission_list_serializer.data
