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

class CreateAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        exclude = ['user']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ['status', 'asset', 'user']