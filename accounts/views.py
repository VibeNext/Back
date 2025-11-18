from django.http import HttpRequest
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import LoginSerializer
from .services import JWTService

class Login(APIView):
    def post(self, request:HttpRequest, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        jwt_service = JWTService()
        data = jwt_service.post(user)

        return Response(
            status=status.HTTP_200_OK,
            data=data,
        )
