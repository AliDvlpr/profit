from django.contrib import admin
from .models import *
from .services import process_confirmed_transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0

    fields = ['action', 'amount', 'status']
    readonly_fields = ('action','amount')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['user','amount', 'level', 'confirmed_at']
    list_select_related = ['user', 'level']
    inlines = [TransactionInline]
    search_fields = ['user']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'profit_rate', 'min_refferral', 'min_deposit']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['asset', 'action', 'amount', 'status', 'updated_at', 'created_at']
    list_editable = ['status']

    def save_model(self, request, obj, form, change):
        original_obj = self.model.objects.get(pk=obj.pk)

        if obj.status == Transaction.STATUS_CONFIRMED and obj.status != original_obj.status:
            process_confirmed_transaction(obj)

            super().save_model(request, obj, form, change)

        super().save_model(request, obj, form, change)