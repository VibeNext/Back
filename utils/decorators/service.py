from functools import wraps
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

def validate_data(service_func):
    """
    클라이언트가 전송한 데이터가 유효한지 검증합니다.
    """
    @wraps(service_func)
    def wrapper(self, *args, **kwargs):
        if not self.serializer.is_valid():
            raise ValidationError(self.serializer.errors)
        return service_func(self, *args, **kwargs)
    return wrapper

def validate_unique(service_func):
    """
    클라이언트의 요청이 UNIQUE 제약조건을 준수하는지 검증합니다.
    """
    @wraps(service_func)
    def wrapper(self, *args, **kwargs):
        try:
            return service_func(self, *args, **kwargs)
        except IntegrityError as error:
            if "UNIQUE constraint failed" in str(error):
                raise Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"detail":"이미 존재하는 값이에요."},
                )
    return wrapper
