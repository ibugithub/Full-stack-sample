from django.core.mail import send_mail
from django.conf import settings


def send_email(subject, recipient_list, message):
  from_email = settings.DEFAULT_FROM_EMAIL
  
  if not recipient_list:
    raise ValueError("Recipient list is empty")
  
  try:
    send_mail(
      subject=subject,
      message=message,
      from_email=from_email,
      recipient_list=recipient_list,
      fail_silently=False,
    )
  except Exception as e:
    raise RuntimeError(f"Failed to send email: {e}")
