from datetime import timedelta

from celery.app import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from bot.bot_util import send_message
from bot.models.cheque import Cheque
from bot.models.user_state import UserState
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


@shared_task
def send_notify_to_users():
    users = UserState.objects.all()
    for user in users:
        send_message_to_user.delay(user.chat_id, "message")


@shared_task
def send_message_to_user(chat_id, message):
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': message
    })


@shared_task
def remind_about_cheque():
    last_month = now() - timedelta(days=30)
    users = UserState.objects.filter(is_registered=True)

    for user in users:
        last_receipt = Cheque.objects.filter(user=user).order_by(
            '-uploaded_at').first()

        if not last_receipt or last_receipt.uploaded_at < last_month:
            send_message("sendMessage", {
                'chat_id': user.chat_id,
                'text': "Пожалуйста, загрузите новый чек за текущий месяц!"
            })
