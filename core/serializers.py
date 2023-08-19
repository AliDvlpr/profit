from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import CustomUser
from wallet.models import Asset
from wallet.serilaizers import AssetSerializer
from django.utils import timezone
from decimal import Decimal

class UserCreateSerializer(BaseUserCreateSerializer):
    referral_token = serializers.CharField(write_only=True) 
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'email', 'password', 'referral_token']

    def create(self, validated_data):
        referral_token = validated_data.pop('referral_token', None)
        referrer = None

        if referral_token:
            try:
                referrer = CustomUser.objects.get(referral_token=referral_token)
            except CustomUser.DoesNotExist:
                pass

        user = CustomUser.objects.create_user(**validated_data, referrer=referrer)

        Asset.objects.create(user=user)

        return user
    
class UserSerializer(BaseUserSerializer):
    asset = AssetSerializer(read_only=True)
    class Meta(BaseUserSerializer.Meta):
        fields = '__all__'

class ReferredUserSerializer(serializers.ModelSerializer):
    confirmed = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = CustomUser
        fields = ['email', 'date_joined', 'confirmed']

    def get_confirmed(self, instance):
        return instance.asset.confirmed_at is not None
    
class UserDashboardSerializer(BaseUserSerializer):
    user_email = serializers.CharField(source='email')  # Access email directly from CustomUser model
    amount = serializers.DecimalField(source='asset.amount', max_digits=12, decimal_places=6)
    level_name = serializers.CharField(source='asset.level.name', allow_null=True)
    profit_rate = serializers.DecimalField(source='asset.level.profit_rate', max_digits=12, decimal_places=6, allow_null=True)
    calculated_profit = serializers.SerializerMethodField(allow_null=True)
    user_credit = serializers.IntegerField(source='credit')
    referral_token = serializers.CharField()
    referrals_count = serializers.SerializerMethodField()  
    active_referrals_count = serializers.SerializerMethodField()
    referrals = serializers.SerializerMethodField()

    def get_referrals_count(self, instance):
        referrals_count = CustomUser.objects.filter(referrer=instance.id).count()
        return referrals_count
    
    def get_active_referrals_count(self, instance):
        referrals = CustomUser.objects.filter(referrer=instance.id)
        filtered_referrals = referrals.filter(
            asset__confirmed_at__isnull=False,
            asset__level__isnull=False
        )
        referrals_count = filtered_referrals.count()
        return referrals_count

    def get_calculated_profit(self, instance):
        asset = instance.asset
        confirmed_at = asset.confirmed_at
        now = timezone.now()

        if confirmed_at is None:
            return 0

        time_difference = now - confirmed_at
        time_difference_in_seconds = time_difference.days

        calculated_profit = Decimal(asset.amount) * Decimal(asset.level.profit_rate) * Decimal(time_difference_in_seconds)
        return calculated_profit

    def get_referrals(self, instance):
        referrals = CustomUser.objects.filter(referrer=instance)
        serializer = ReferredUserSerializer(referrals, many=True)
        return serializer.data
    
    class Meta:
        model = CustomUser
        fields = ['user_email', 'amount', 'level_name','profit_rate', 'calculated_profit', 'user_credit', 'referral_token', 'referrals_count', 'active_referrals_count', 'referrals']
