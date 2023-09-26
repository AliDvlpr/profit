from django.contrib import admin
from django import forms 
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
from django.urls import path
from datetime import datetime, timedelta
from .models import *
from wallet.models import *
from wallet.services import process_confirmed_transaction
from django.db.models import Max

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
        (None, {'fields': ('email', 'password', 'is_active', 'credit','chat_link')}),
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

    readonly_fields = ('chat_link',)  # Mark the chat_link as read-only

    def chat_link(self, obj):
        url = reverse('admin:core_chat_change', args=[obj.chat.id])
        return format_html('<a href="{}">Open Chat</a>', url)

    chat_link.short_description = 'Chat'

    actions = ['open_user_chat']

    def open_user_chat(self, request, queryset):
        for user in queryset:
            if user.chat:
                chat_url = reverse('admin:core_chat_change', args=[user.chat.id])
                self.message_user(request, f'Chat for user {user} opened at {chat_url}.')
            else:
                self.message_user(request, f'User {user} does not have a chat.')

    open_user_chat.short_description = 'Open Chat for Selected Users'

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 1
    fields = ('content', 'user')
    list_filter = ['status']

    def has_delete_permission(self, request, obj=None):
        return False 
    
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'last_message']
    inlines = [ChatMessageInline]
    actions = ['add_chat_message']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_admin_chat'] = True

        chat = Chat.objects.get(pk=object_id)
        chat_messages = chat.chatmessage_set.all().order_by('timestamp')

        extra_context['chat'] = chat
        extra_context['chat_messages'] = chat_messages

        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def last_message(self, obj):
        last_message = obj.chatmessage_set.aggregate(last_message_timestamp=Max('timestamp'))
        return last_message['last_message_timestamp']

    last_message.admin_order_field = 'last_message'
    
    def get_queryset(self, request):
        # Override the default queryset to order by last_message_timestamp in descending order
        # and exclude chats with status set to 'Nothing' ('N').
        return super().get_queryset(request).annotate(
            last_message_timestamp=Max('chatmessage__timestamp')
        ).exclude(status=Chat.STATUS_NOTHING).order_by('-last_message_timestamp')
    
    change_form_template = 'admin_chat_page.html'