"""
URL configurations mapping identity controls, registration pathways, 
profile interfaces, and secure password lifecycle overrides.
"""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Master Authentication Pathways
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    #path("register/", views.UserRegisterView.as_view(), name="register"),
    
    # Extended Workspace Profile Pathways
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("profile/update/", views.UserProfileUpdateView.as_view(), name="profile_update"),
    
    # Email Verification Pathways
    path("verify-email/confirm/<str:token>/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("verify-email/trigger/", views.VerifyEmailTriggerView.as_view(), name="verify_email_trigger"),

    # Hardened Password Reset Pathways
    path("password-reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]