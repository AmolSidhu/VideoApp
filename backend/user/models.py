from django.db import models
from django.contrib.auth.models import AbstractUser

class Credentials(AbstractUser):
    email = models.EmailField(unique=True, max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    verification_code = models.CharField(max_length=100, default='')
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    permission = models.IntegerField(default=2)
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']
    
    class Meta:
        db_table = 'credentials'
        verbose_name = 'Credentials'
        verbose_name_plural = 'Credentials' 