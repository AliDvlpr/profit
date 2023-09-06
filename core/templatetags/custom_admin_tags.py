from django import template
from core.models import Chat
from wallet.models import Transaction

register = template.Library()

@register.simple_tag
def pending_messages_count():
    return Chat.objects.filter(status='P').count()

@register.simple_tag
def pending_deposits_count():
    return Transaction.objects.filter(action='D', status='P').count()

@register.simple_tag
def pending_withdraws_count():
    return Transaction.objects.filter(action='W', status='P').count()
