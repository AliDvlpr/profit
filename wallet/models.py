from django.db import models
from core.models import CustomUser

# Create your models here.
class Asset(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="asset")
    level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"Asset for {self.user.email}"
    
class Level(models.Model):
    name = models.CharField("Level Name", max_length=128)
    profit_rate = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    min_referral = models.IntegerField(default=0)
    min_deposit = models.DecimalField(max_digits=12, decimal_places=6, default=0)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    ACTION_DEPOSIT = 'D'
    ACTION_WITHDRAW = 'W'
    ACTION_PROFIT = 'P'
    ACTION_CHOICES = [
        (ACTION_DEPOSIT, 'Deposit'),
        (ACTION_WITHDRAW, 'Withdraw'),
        (ACTION_PROFIT, 'Profit')
    ]
    action = models.CharField(
        max_length=1, choices=ACTION_CHOICES, default=ACTION_DEPOSIT)
    amount = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    STATUS_PENDING = 'P'
    STATUS_CONFIRMED = 'C'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_REJECTED, 'Rejected')
    ]
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="transactions")
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Transactions of {self.asset.user.email}"
    
    class Meta:
        ordering = ['-created_at']

class Setting(models.Model):
    wallet_address = models.CharField(max_length=255)