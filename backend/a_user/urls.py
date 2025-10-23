from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ChangePasswordAPIView, SendResetEmailAPIView, ResetPasswordAPIView, CustomTokenObtainPairView, SendVerificationEmail, VerifyEmail, ValidadeToken


urlpatterns = [
    #auth
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("validate-token/", ValidadeToken.as_view(), name="validate_token"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("send-reset-email/", SendResetEmailAPIView.as_view(), name="send_reset_email"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset_password"), 
    path("send-verification-email/", SendVerificationEmail.as_view(), name="send_verification_email"),
    path("verify-email/", VerifyEmail.as_view(), name="verify_email"),
]

