from django.db import models
from core.models import CustomUser

# Create your models here.
class Asset(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    level = models.ForeignKey('Level', on_delete=models.SET_NULL, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"Asset for {self.user.email}"
    
class Level(models.Model):
    name = models.CharField("Level Name", max_length=128)
    profit_rate = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    min_refferral = models.IntegerField(default=0)
    min_deposit = models.DecimalField(max_digits=9, decimal_places=6, default=0)