from django.contrib import admin
from .models import *

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['user','amount', 'level', 'confirmed_at']
    list_select_related = ['user', 'level']
    search_fields = ['user']

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'profit_rate', 'min_refferral', 'min_deposit']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # ... other attributes ...

    def save_model(self, request, obj, form, change):
        original_obj = self.model.objects.get(pk=obj.pk)

        if obj.status == Transaction.STATUS_CONFIRMED and obj.status != original_obj.status:
            if obj.action == Transaction.ACTION_DEPOSIT:
                # Add the amount to the asset
                obj.asset.amount += obj.amount
            elif obj.action == Transaction.ACTION_WITHDRAW:
                # Subtract the amount from the asset
                obj.asset.amount -= obj.amount

            # Save the updated asset
            obj.asset.save()

        super().save_model(request, obj, form, change)