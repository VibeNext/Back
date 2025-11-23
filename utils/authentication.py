from rest_framework_simplejwt.authentication import JWTAuthentication

class OptionalJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None
