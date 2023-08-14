from rest_framework import serializers
from .models import *

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class CreateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ['status', 'asset', 'user']