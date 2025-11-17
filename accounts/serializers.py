from django.contrib.auth import authenticate
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(detail='이메일 또는 비밀번호가 일치하지 않아요.')
        if not user.is_active:
            raise serializers.ValidationError(detail='비활성화된 계정이에요.')

        attrs['user'] = user
        return attrs
