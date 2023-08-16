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
        referrer = validated_data.pop('referrer', None)  # Get the referrer value from validated_data
        user = CustomUser.objects.create_user(**validated_data, referrer=referrer)

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
    profit_rate = serializers.DecimalField(source='asset.level.profit_rate', max_digits=12, decimal_places=6)
    calculated_profit = serializers.SerializerMethodField()
    user_credit = serializers.IntegerField(source='credit')
    referral_token = serializers.CharField()
    referred_users_count = serializers.SerializerMethodField()  

    def get_referred_users_count(self, instance):
        referred_users_count = CustomUser.objects.filter(referrer=instance.referral_token).count()
        return referred_users_count

    def get_calculated_profit(self, instance):
        asset = instance.asset
        confirmed_at = asset.confirmed_at
        now = timezone.now()

        time_difference = now - confirmed_at
        time_difference_in_seconds = time_difference.days

        calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference_in_seconds)
        return calculated_profit

    class Meta:
        model = CustomUser
        fields = ['user_email', 'amount', 'level_name','profit_rate', 'calculated_profit', 'user_credit', 'referral_token', 'referred_users_count']
