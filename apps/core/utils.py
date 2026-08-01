import threading
from django.core.mail import send_mail


def send_mail_background(subject, message, from_email, recipient_list):
    def send():
        try:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=True,
            )
        except Exception:
            pass

    threading.Thread(
        target=send,
        daemon=True
    ).start()