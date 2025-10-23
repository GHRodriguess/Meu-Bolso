from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import ChangePasswordSerializer, SendResetEmailSerializer, ResetPasswordConfirmSerializer, CustomTokenObtainPairSerializer, SendVerificationEmailSerializer, VerifyEmailSerializer
from a_email.services import send_reset_password_email, send_verification_email
from dotenv import load_dotenv
from django.conf import settings
import os    
from rest_framework_simplejwt.views import TokenObtainPairView


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SendResetEmailAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SendResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            load_dotenv() 
            user, token = serializer.save()
            if settings.DEBUG: 
                base_url_frontend = os.getenv("BASE_URL_FRONTEND_DEVELOPMENT")
            else:
                base_url_frontend = os.getenv("BASE_URL_FRONTEND_PRODUCTION")

            reset_link = f"{base_url_frontend}/change-password/?token={token}"
            
            send_reset_password_email(user, reset_link)

            return Response({"detail": "E-mail de redefinição de senha enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
            
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

class SendVerificationEmail(APIView):
    
    def post(self, request):
        serializer = SendVerificationEmailSerializer(data=request.data)
        if serializer.is_valid():
            load_dotenv() 
            user, token = serializer.save()
            if settings.DEBUG: 
                base_url_frontend = os.getenv("BASE_URL_FRONTEND_DEVELOPMENT")
            else:
                base_url_frontend = os.getenv("BASE_URL_FRONTEND_PRODUCTION")
            verification_link = f"{base_url_frontend}/verify-email/?token={token}"
            send_verification_email(user, verification_link)
            return Response({"detail": "E-mail de redefinição de senha enviado."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmail(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "E-mail verificado com sucesso."}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ValidadeToken(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        try:
            token_obj = AccessToken(token) 
            return Response({"valid": True})
        except (InvalidToken, TokenError):
            return Response({"valid": False}, status=401)