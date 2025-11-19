from django.http import HttpRequest
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .services import MissionService

class Root(APIView):
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def get(self, request:HttpRequest, format=None):
        mission_service = MissionService(request)

        if request.user.is_authenticated:
            data = {'test':'인증됨! 토큰 유효함!'}
        else:
            data = mission_service.get_list()

        return Response(
            status=status.HTTP_200_OK,
            data=data,
        )
