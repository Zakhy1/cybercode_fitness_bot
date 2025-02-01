from celery.app import shared_task
from django.core.mail import send_mail

from project.settings import EMAIL_HOST_USER




@shared_task
def send_email(email, code):
    subject = "Код подтверждения для регистрации"
    message = f"Ваш код подтверждения: {code}"
    recipient_list = [email]

    try:
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list)
        print(f"Код отправлен на {email}")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
