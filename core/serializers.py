from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import CustomUser
from wallet.models import Asset

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'password', 'referrer']

    def create(self, validated_data):
        referrer = None
        if 'referrer' in validated_data:
            referrer = validated_data.pop('referrer')

        user = super().create(validated_data)

        Asset.objects.create(user=user)

        return user