from datetime import timedelta

from celery.app import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from bot.bot_util import send_message
from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState
from project.settings import EMAIL_HOST_USER
from settings.models import Settings


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
    # Создание отчета
    today = now().date()
    first_day_of_current_month = today.replace(day=1)
    first_day_of_previous_month = (
            first_day_of_current_month - timedelta(days=1)).replace(day=1)
    start_str = first_day_of_previous_month.strftime("%d.%m.%Y")
    required_count = int(Settings.get_setting("circle_required_count", "4"))
    host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")

    report = [
        {
            "chat_id": 389838514,
            "text": f"Отчет от {start_str}",
        }
    ]

    users = UserState.objects.all()

    for user in users:
        # Отсеиваем
        if not user.is_registered:
            print(f"{user.name} - Не зарегистрирован")
            continue
        if not user.has_contract:
            print(f"{user.name} - Не имеет договор")
            continue
        user_circes_count = Circle.objects.filter(
            uploaded_at__gte=first_day_of_previous_month,
            user=user).count()
        if user_circes_count < required_count:
            print(
                f"{user.name} - Количество кружок {user_circes_count}, а необходимо: {required_count} ")
            continue
        try:
            latest_cheque = Cheque.objects.filter(
                uploaded_at__gte=first_day_of_previous_month,
                user=user).latest("uploaded_at")
        except Cheque.DoesNotExist:
            existent_cheque = Cheque.objects.filter(user=user).order_by(
                "uploaded_at").last()
            if existent_cheque.exists():
                print(
                    f"{user.name} - Нет чека за месяц (Последний от {existent_cheque.uploaded_at})")
            else:
                print(f"{user.name} - Нет чека за месяц")
            continue
        # Добавляем в отчет
        latest_contract = Contract.objects.latest('uploaded_at')
        report.append({
            "chat_id": int(Settings.get_setting("admin_chat_id", "389838514")),
            "text": user.get_name(),
            "disable_notification": True,
            "reply_markup": {
                "inline_keyboard": [
                    [{
                        "text": "📥 Договор",
                        "url": f'{host_url}{latest_contract.file.url}',
                    }],
                    [{
                        "text": "📥 Последний чек",
                        "url": f'{host_url}{latest_cheque.file.url}',
                    }]
                ]
            }
        })
    for row in report:
        send_message_to_user_generic.delay(row)

