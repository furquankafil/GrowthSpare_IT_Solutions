import threading
from django.core.mail import send_mail


def send_mail_background(subject, message, from_email, recipient_list, **kwargs):
    """Send email in a separate thread so form handling remains non-blocking."""

    def _send():
        try:
            send_mail(subject, message, from_email, recipient_list, **kwargs)
        except Exception:
            # Ensure background email failures do not affect the primary request.
            pass

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    return thread
