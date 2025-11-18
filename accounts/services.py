from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from utils.helpers import format_timestamp_iso

class JWTService:
    def post(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        return {
            'grant_type': api_settings.AUTH_HEADER_TYPES[0],
            'access': {
                'token': str(access_token),
                'expire_at': format_timestamp_iso(access_token['exp']),
            },
            'refresh': {
                'token': str(refresh_token),
                'expire_at': format_timestamp_iso(refresh_token['exp']),
            },
        }
