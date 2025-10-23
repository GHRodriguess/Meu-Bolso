from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O usuário deve ter um email')
        email = self.normalize_email(email)
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = email.split('@')[0]  
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(
        'endereço de e-mail', 
        unique=True,         
        blank=False,   
        null=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    
    
    objects = CustomUserManager()
    
    verified_email = models.BooleanField(default=False)
    need_change_password = models.BooleanField(default=False)
    reset_password_token = models.CharField(max_length=64, blank=True, null=True)
    reset_password_token_created_at = models.DateTimeField(blank=True, null=True)
    verified_email_token = models.CharField(max_length=64, blank=True, null=True)
