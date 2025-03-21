import traceback
from datetime import timedelta

from celery.app import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from bot.models.cheque import Cheque
from bot.models.user_state import UserState
from project.logging_settings import info_logger, error_logger
from project.settings import EMAIL_HOST_USER, TELEGRAM_API_URL
from settings.models import Settings
import requests

# info_logger.info("Это информационное сообщение1")


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
    except Exception:
        error_logger.error(traceback.format_exc())


@shared_task
def send_message_to_user(chat_id, message):
    try:
        send_message("sendMessage", {
            'chat_id': chat_id,
            'text': message,
        })
    except Exception:
        error_logger.error(traceback.format_exc())


@shared_task
def send_message_to_user_generic(obj):
    try:
        send_message("sendMessage", obj)
    except Exception:
        error_logger.error(traceback.format_exc())


@shared_task
def remind_about_cheque():
    try:
        last_month = now().replace(day=1)
        users = UserState.objects.filter(is_registered=True)

        for user in users:
            try:
                last_receipt = Cheque.objects.latest('uploaded_at')
            except Cheque.DoesNotExist:
                continue
            if last_receipt.uploaded_at < last_month:
                send_message_to_user.delay(
                    user.chat_id,
                    "Пожалуйста, загрузите новый чек за текущий месяц!"
                )
    except Exception:
        error_logger.error(traceback.format_exc())
