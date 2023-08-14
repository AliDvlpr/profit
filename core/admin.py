from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser
from wallet.models import *

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ['action', 'amount', 'status']
    readonly_fields = ('action','amount')

class AssetInline(admin.StackedInline):
    model = Asset
    fields = ('amount', 'level', 'confirmed_at', 'asset')
    readonly_fields = ('amount', 'level', 'asset')
    extra = 0

    def asset(self, instance):
        if instance.pk:
            change_url = reverse('admin:wallet_asset_change', args=[instance.pk])
            return format_html('<a href="{}">Open Asset</a>', change_url)
        return ''
    
    asset.short_description = 'Asset'

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'referrer', 'asset_amount']
    inlines = [AssetInline, TransactionInline]

    def asset_amount(self, obj):
        return obj.asset.amount if obj.asset else None
  
    asset_amount.short_description = 'Asset Amount'