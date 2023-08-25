from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import *
from wallet.models import *
from wallet.serilaizers import *
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum


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
        Chat.objects.create(user=user)

        return user
    
class UserSerializer(BaseUserSerializer):
    asset = AssetSerializer(read_only=True)
    class Meta(BaseUserSerializer.Meta):
        fields = '__all__'

class ReferredUserSerializer(serializers.ModelSerializer):
    confirmed = serializers.SerializerMethodField()
    referral_profit_rate = serializers.SerializerMethodField()
    calculated_referral_profit = serializers.SerializerMethodField()
    asset = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    date_joined = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = CustomUser
        fields = ['email', 'date_joined', 'referral_profit_rate', 'calculated_referral_profit', 'asset', 'level', 'confirmed']

    def get_confirmed(self, instance):
        return instance.asset.confirmed_at is not None
    
    def get_referral_profit_rate(self, instance):
        asset = instance.asset
        if asset.level is not None:
            return asset.level.referral_profit_rate
        else:
            return 0
        
    def get_calculated_referral_profit(self, instance):
        asset = instance.asset
        referral_profit_rate = self.get_referral_profit_rate(instance)
        
        if asset.confirmed_at is not None and referral_profit_rate > 0:
            now = timezone.now()
            time_difference = now - asset.confirmed_at

            calculated_referral_profit = Decimal(referral_profit_rate) * Decimal(time_difference.days)
            return calculated_referral_profit
        
        return 0
    
    def get_asset(self, instance):
        return instance.asset.amount if instance.asset else None

    def get_level(self, instance):
        return instance.asset.level.name if instance.asset and instance.asset.level else None
        

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
    referrals = serializers.SerializerMethodField(allow_null=True)
    total_profit = serializers.SerializerMethodField()
    total_referral_profit = serializers.SerializerMethodField()

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
    
    def get_total_profit(self, instance):
        user = instance
        asset = user.asset

        # Calculate total profit from transactions with action=profit and asset=user's asset
        total_profit = Transaction.objects.filter(
            action=Transaction.ACTION_PROFIT,
            asset=asset,
            user=user
        ).aggregate(total_profit=Sum('amount'))['total_profit']

        return total_profit or 0
    
    def get_total_referral_profit(self, instance):
        user = instance
        asset = user.asset

        # Calculate total referral profit from transactions with action=profit, asset=user's asset, and user is not the current user
        total_referral_profit = Transaction.objects.filter(
            action=Transaction.ACTION_PROFIT,
            asset=asset
        ).exclude(user=user).aggregate(total_referral_profit=Sum('amount'))['total_referral_profit']

        return total_referral_profit or 0 
    
    class Meta:
        model = CustomUser
        fields = ['user_email', 'amount', 'level_name',
                  'profit_rate', 'calculated_profit', 'user_credit', 
                  'referral_token', 'referrals_count', 'active_referrals_count', 
                  'total_profit', 'total_referral_profit', 'referrals']

class ChatMessageSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)

    def get_user_email(self, instance):
        return instance.user.email
    
    class Meta:
        model = ChatMessage
        fields = ['content','timestamp', 'user_email']

class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['content', 'chat', 'user']
