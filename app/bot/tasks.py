from datetime import timedelta

from celery.app import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from bot.models.cheque import Cheque
from bot.models.report import Report
from bot.models.user_state import UserState
from project.logging_settings import info_logger, error_logger
from project.settings import EMAIL_HOST_USER, TELEGRAM_API_URL
from settings.models import Settings
import requests

info_logger.info("Это информационное сообщение1")
error_logger.error("Это сообщение об ошибке1")


def send_message(method, data):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + '/' + method
    response = requests.post(url, json=data)
    return response


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


@shared_task
def send_message_to_user(chat_id, message):
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': message,
    })


@shared_task
def send_message_to_user_generic(obj):
    send_message("sendMessage", obj)


@shared_task
def remind_about_cheque():
    last_month = now() - timedelta(days=30)
    users = UserState.objects.filter(is_registered=True)

    for user in users:
        last_receipt = Cheque.objects.filter(user=user).order_by(
            '-uploaded_at').first()

        if not last_receipt or last_receipt.uploaded_at < last_month:
            send_message_to_user.delay(
                user.chat_id,
                "Пожалуйста, загрузите новый чек за текущий месяц!"
            )


@shared_task
def make_report():
    info_logger.info("Это информационное сообщение1")
    error_logger.error("Это сообщение об ошибке1")

    Report.create_and_send()
