from rest_framework import serializers
from .models import *

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class AssetSerializer(serializers.ModelSerializer):
    level = LevelSerializer(read_only=True)
    class Meta:
        model = Asset
        fields = '__all__'

class UpdateAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["level"]

class TransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    class Meta:
        model = Transaction
        fields = '__all__'
        

class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ['status', 'asset', 'user', 'created_at', 'updated_at']

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = "__all__"