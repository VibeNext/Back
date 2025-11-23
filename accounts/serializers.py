from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','password','name','profile_image',)
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data:dict):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'invalid_credentials':'이메일 또는 비밀번호가 일치하지 않아요.'})

        if not user.check_password(password):
            raise serializers.ValidationError({'invalid_credentials':'이메일 또는 비밀번호가 일치하지 않아요.'})

        if not user.is_active:
            raise serializers.ValidationError({'inactive_account':'비활성화된 계정이에요.'})

        attrs['user'] = user
        return attrs
