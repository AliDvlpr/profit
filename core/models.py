import random
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email,username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, referrer=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        if referrer:
            extra_fields['referrer'] = referrer

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if email is None:
            raise ValueError('The Email field must be set for superuser.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    credit = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    referral_token = models.CharField(max_length=6,null=True, blank=True)
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    objects = CustomUserManager() 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def generate_unique_referral_token(self):
        while True:
            return ''.join(random.choices('0123456789', k=6))
    
    def save(self, *args, **kwargs):
        if not self.referral_token and not self.id:
            while True:
                referral_token = self.generate_unique_referral_token()
                if not CustomUser.objects.filter(referral_token=referral_token).exists():
                    self.referral_token = referral_token
                    break
        super().save(*args, **kwargs)

class Chat(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    STATUS_PENDING = 'P'
    STATUS_ANSWERED = 'A'
    STATUS_NOTHING = 'N'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ANSWERED, 'Answered'),
        (STATUS_NOTHING, 'Nothing')
    ]
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=STATUS_NOTHING)

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True) 