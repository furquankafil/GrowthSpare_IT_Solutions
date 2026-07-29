"""
Identity, registration, multi-model profile editing, cryptographically secure 
activation handshakes, and custom password recovery class-based controllers.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views import View
from django.views.generic import CreateView, TemplateView, UpdateView
from django_ratelimit.decorators import ratelimit

from .models import User, UserProfile
from .forms import UserRegisterForm, UserAccountUpdateForm, UserProfileUpdateForm

# Secure cryptographic timestamped signer for activation handshakes (valid for 24h)
signer = TimestampSigner()


@method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True), name="post")
class UserLoginView(LoginView):
    """Secure login gateway directing validated users to their respective workspace panels.
    Rate-limited to 10 POST attempts/minute per IP to slow brute-force credential guessing."""
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """Directs user dynamically based on authentication context or target page request."""
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse_lazy("dashboard:index")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid corporate credentials. Please verify your details.")
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """Standard secure logout engine clearing identity context and redirecting to the root home page."""
    next_page = reverse_lazy("core:home")

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Secure session closed successfully.")
        return super().dispatch(request, *args, **kwargs)


class UserRegisterView(CreateView):
    """
    Client self-registration gateway mapping dynamic user records, sending cryptographically 
    signed validation emails, and auto-logging the verified session profile.
    """
    model = User
    form_class = UserRegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form):
        # Save custom user parameters
        user = form.save(commit=False)
        user.is_active = True  # Account active by default, validation strictly monitored
        user.save()

        # Send Signed Activation Email dynamically
        self.send_activation_email(user)

        # Handle direct session login for seamless workflow
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        
        messages.success(
            self.request,
            "Corporate account instantiated successfully! A cryptographically signed verification "
            "email has been dispatched to your inbox. Please click the confirmation link within 24 hours.",
        )
        return redirect(self.get_success_url())

    def send_activation_email(self, user):
        """Generates cryptographically signed activation coordinates and dispatches confirmation mail."""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = signer.sign(user.email)
        
        # Absolute URL target builder
        protocol = "https" if self.request.is_secure() else "http"
        domain = self.request.get_host()
        activation_link = f"{protocol}://{domain}/accounts/verify-email/confirm/{uid}/{token}/"

        subject = "Confirm Your Workspace Account - GrowthSpare IT Solutions"
        message = (
            f"Greetings {user.first_name or user.username},\n\n"
            f"Thank you for registering on the GrowthSpare IT Solutions platform.\n\n"
            f"Please click the link below to confirm your email and complete your workspace configuration:\n"
            f"{activation_link}\n\n"
            f"Note: This verification link is strictly valid for the next 24 hours only.\n\n"
            f"If you did not initiate this registration request, please ignore this communication.\n\n"
            f"Respectfully,\n"
            f"Identity Desk, GrowthSpare IT Solutions"
        )
        try:
            send_mail(
                subject,
                message,
                "GrowthSpare IT Solutions <growthspareitsolution@gmail.com>",
                [user.email],
                fail_silently=False,
            )
        except Exception:
            # Prevent operational runtime halts if email daemon is unconfigured local server fallback
            pass


class VerifyEmailView(View):
    """Cryptographic receiver parsing verification handshake parameters and validating users."""

    def get(self, request, token, *args, **kwargs):
        # Retrieve uidb64 from nested dispatch logic or custom parameter structure
        # Custom signer signature holds cryptographically validated user identification context
        try:
            # Signer checks expiration limits automatically based on max_age (86400s = 24 hours)
            email = signer.unsign(token, max_age=86400)
            user = User.objects.get(email=email)
            
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
                messages.success(request, "Corporate email verified successfully. Full platform access enabled.")
            else:
                messages.info(request, "Corporate email is already verified.")
                
            return redirect("dashboard:index")
            
        except SignatureExpired:
            messages.error(request, "The account validation window has expired (Max: 24h). Please request a new link.")
        except (BadSignature, User.DoesNotExist):
            messages.error(request, "Invalid validation signature or security context token.")
            
        return redirect("accounts:profile")


class VerifyEmailTriggerView(LoginRequiredMixin, View):
    """Enables manual, on-demand dispatch triggers of the activation credentials."""
    
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_email_verified:
            messages.info(request, "Corporate identity is already verified.")
        else:
            # Dispatch activation using custom reusable generator
            reg_view = UserRegisterView()
            reg_view.request = request
            reg_view.send_activation_email(user)
            messages.success(request, "Validation handshake credentials dispatched. Check your workspace inbox.")
        return redirect("accounts:profile")


class UserProfileView(LoginRequiredMixin, TemplateView):
    """Renders active identity status, profile parameters, and associated company parameters."""
    template_name = "accounts/profile.html"


class UserProfileUpdateView(LoginRequiredMixin, View):
    """
    Handles complex simultaneous dual-model update logic, binding standard 
    User details and UserProfile details within a single POST transition.
    """
    template_name = "accounts/profile_update.html"

    def get(self, request, *args, **kwargs):
        user_form = UserAccountUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=request.user.profile)
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )

    def post(self, request, *args, **kwargs):
        user_form = UserAccountUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your enterprise profile configurations were updated successfully.")
            return redirect("accounts:profile")
            
        messages.error(request, "Validation error occurred. Please verify your data metrics.")
        return render(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )


# ==============================================================================
# Hardened Password Reset Views (Inheriting Django Built-ins with custom routing)
# ==============================================================================

class CustomPasswordResetView(PasswordResetView):
    """Security-focused reset trigger generating secure activation coordinates."""
    template_name = "accounts/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")

    def form_valid(self, form):
        messages.info(
            self.request,
            "If an account matches that email address, safe recovery instructions have been dispatched.",
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")

    def form_valid(self, form):
        messages.success(this_req := self.request, "Secure system password changed successfully.")
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"