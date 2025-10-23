from .models import User
from rest_framework import serializers 
from django.utils.crypto import get_random_string
from django.utils import timezone
from a_email.services import send_welcome_email, send_welcome_change_password_email  
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import os 
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {"password": {"write_only": True}}
        
    def create(self, validated_data):
        groups = validated_data.pop('groups', []) 
        permissions = validated_data.pop('user_permissions', [])
        password = validated_data.pop('password', None)
        user = self.Meta.model(**validated_data)
        if password:
            user.set_password(password)            
        user.save()
        if groups:
            user.groups.set(groups)
        if permissions:
            user.user_permissions.set(permissions)        
        
        
        if validated_data.get("need_change_password", False):
            serializer = SendResetEmailSerializer(data={"email": user.email})
            if serializer.is_valid():
                user, token = serializer.save()
                
                if settings.DEBUG: 
                    base_url_frontend = os.getenv("BASE_URL_FRONTEND_DEVELOPMENT")
                else:
                    base_url_frontend = os.getenv("BASE_URL_FRONTEND_PRODUCTION")

                reset_link = f"{base_url_frontend}/change-password/?token={token}"
                
                send_welcome_change_password_email(user, password, reset_link)
        else: 
            send_welcome_email(user) 
        
        return user
    
    
    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        permissions = validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if groups is not None:
            instance.groups.set(groups)
        if permissions is not None:
            instance.user_permissions.set(permissions)
        return instance
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value
    
class SendResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Usuário com este e-mail não existe.")
        return value
    
    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        token = get_random_string(64)
        user.reset_password_token = token
        user.reset_password_token_created_at = timezone.now()
        user.save()
        return user, token
    
class ResetPasswordConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate_token(self, value):
        try:
            user = User.objects.get(reset_password_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")

        if not user.need_change_password and user.reset_password_token_created_at + timezone.timedelta(minutes=15) < timezone.now():
            raise serializers.ValidationError("Token expirado.")

        return value 
    
    def save(self):
        token = self.validated_data['token']
        new_password = self.validated_data['new_password']
        user = User.objects.get(reset_password_token=token)
        user.set_password(new_password)
        user.reset_password_token = None
        user.reset_password_token_created_at = None
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
    
class SendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Usuário com este e-mail não existe.")
        return value
    
    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        token = get_random_string(64)
        user.verified_email_token = token
        user.save()
        return user, token
    
class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def validate_token(self, value):
        try:
            user = User.objects.get(verified_email_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Token inválido.")
        return value 
    
    def save(self):
        token = self.validated_data['token']
        user = User.objects.get(verified_email_token=token)
        user.verified_email = True
        user.verified_email_token = None
        user.save()
        return user