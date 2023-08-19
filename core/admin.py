from django.contrib import admin
from django import forms 
from django.utils.html import format_html
from django.urls import reverse
from .models import CustomUser
from wallet.models import *
from wallet.services import process_confirmed_transaction
from datetime import datetime, timedelta

class ReferredUsersInline(admin.TabularInline):
    model = CustomUser
    fk_name = 'referrer'
    fields = ('email', 'asset_amount', 'credit', 'confirmed_at', 'days_since_confirmation')
    readonly_fields = ('email', 'asset_amount','credit', 'confirmed_at', 'days_since_confirmation')
    extra = 0
    verbose_name = 'Referral'
    verbose_name_plural = 'Referrals'
    can_delete = False

    def email(self, instance):
        return instance.email

    def asset_amount(self, instance):
        return instance.asset.amount if instance.asset else None

    asset_amount.short_description = 'Asset Amount'

    def confirmed_at(self, instance):
        return instance.asset.confirmed_at if instance.asset else None

    confirmed_at.short_description = 'Confirmed At'

    def days_since_confirmation(self, instance):
        confirmed_at = instance.asset.confirmed_at if instance.asset else None
        if confirmed_at:
            days_difference = (datetime.now().date() - confirmed_at.date()).days
            return days_difference
        return None

    days_since_confirmation.short_description = 'Days Since Confirmation'

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ['action', 'amount', 'status', 'updated_at', 'created_at', 'transaction']
    readonly_fields = ('action','amount', 'status', 'transaction', 'updated_at', 'created_at')
    can_delete = False

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

class AssetInlineForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmed_at'].required = False

class AssetInline(admin.StackedInline):
    model = Asset
    form = AssetInlineForm
    fields = ('amount', 'level', 'confirmed_at')
    readonly_fields = ('amount', 'level')
    extra = 0

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_active', 'credit')}),
        ('referral info', {'fields':('referral_token','referrer')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Make this user an admin', {'fields': ('is_staff',)})
    )

    list_display = ['email', 'referrer', 'asset_amount', 'credit', 'confirmed_at', 'days_since_confirmation']
    inlines = [AssetInline, TransactionInline, ReferredUsersInline]
    search_fields = ['email']

    def asset_amount(self, obj):
        return obj.asset.amount if obj.asset else None
  
    asset_amount.short_description = 'Asset Amount'

    def confirmed_at(self, obj):
        return obj.asset.confirmed_at if obj.asset else None

    confirmed_at.short_description = 'Confirmed At'

    def days_since_confirmation(self, obj):
        confirmed_at = obj.asset.confirmed_at if obj.asset else None
        if confirmed_at:
            days_difference = (datetime.now().date() - confirmed_at.date()).days
            return days_difference
        return None

    days_since_confirmation.short_description = 'Days Since Confirmation'