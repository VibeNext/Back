from django.http import HttpRequest
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import MissionService

class Root(APIView):
    def get(self, request:HttpRequest, format=None):
        mission_service = MissionService(request)
        data = mission_service.get_list()

        return Response(
            status=status.HTTP_200_OK,
            data=data,
        )
