from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import CustomUser
from wallet.models import Asset
from wallet.serilaizers import AssetSerializer
from django.utils import timezone
from decimal import Decimal

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
    
class UserSerializer(BaseUserSerializer):
    asset = AssetSerializer(read_only=True)
    class Meta(BaseUserSerializer.Meta):
        fields = '__all__'

class UserDashboardSerializer(BaseUserSerializer):
    user_email = serializers.CharField(source='email')  # Access email directly from CustomUser model
    amount = serializers.DecimalField(source='asset.amount', max_digits=12, decimal_places=6)
    level_name = serializers.CharField(source='asset.level.name')
    calculated_profit = serializers.SerializerMethodField()
    user_credit = serializers.IntegerField(source='credit')

    def get_calculated_profit(self, instance):
        asset = instance.asset
        confirmed_at = asset.confirmed_at
        now = timezone.now()

        time_difference = now - confirmed_at
        time_difference_in_seconds = time_difference.total_seconds()

        calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference_in_seconds)
        return calculated_profit

    class Meta:
        model = CustomUser
        fields = ['user_email', 'amount', 'level_name', 'calculated_profit', 'user_credit']
