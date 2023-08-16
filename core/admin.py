from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser
from wallet.models import *
from wallet.services import process_confirmed_transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ['action', 'amount', 'status', 'updated_at', 'created_at', 'transaction']
    readonly_fields = ('action','amount', 'status', 'transaction', 'updated_at', 'created_at')

    def transaction(self, instance):
        if instance.pk:
            change_url = reverse('admin:wallet_transaction_change', args=[instance.pk])
            return format_html('<a href="{}">Details</a>', change_url)
        return ''
    
    transaction.short_description = 'transaction'

    def save_model(self, request, obj, form, change):
        original_obj = self.model.objects.get(pk=obj.pk)

        if obj.status == Transaction.STATUS_CONFIRMED and obj.status != original_obj.status:
            process_confirmed_transaction(obj)

            super().save_model(request, obj, form, change)

        super().save_model(request, obj, form, change)

class AssetInline(admin.StackedInline):
    model = Asset
    fields = ('amount', 'level', 'confirmed_at')
    readonly_fields = ('amount', 'level')
    extra = 0

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_active', 'credit')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Make this user an admin', {'fields': ('is_staff',)})
    )

    list_display = ['email', 'referrer', 'asset_amount']
    inlines = [AssetInline, TransactionInline]

    def asset_amount(self, obj):
        return obj.asset.amount if obj.asset else None
  
    asset_amount.short_description = 'Asset Amount'