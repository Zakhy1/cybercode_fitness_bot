import datetime
import json
import random
import traceback

from django.http import HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from bot.bot_util import send_message, save_circle, \
    download_and_save_telegram_file, get_main_keyboard, validate_name, \
    is_corporate_email, calc_timedelta_between_dates
from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.report import Report
from bot.models.user_state import UserState
from bot.tasks import send_email, send_message_to_user_generic
from project.settings import TELEGRAM_API_URL
from settings.models import Settings
import requests
from django.utils import timezone


@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        message = json.loads(request.body.decode('utf-8'))
        if "callback_query" in message:
            return handle_callback_query(message)
        chat_id = message['message']['chat']['id']
        text = message['message'].get('text', '')

        user_state, _ = UserState.objects.get_or_create(chat_id=chat_id)

        # Обработка команды /start
        if text == '/start':
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Добро пожаловать! Пожалуйста, выберите действие:",
                'reply_markup': json.dumps({
                    "keyboard": [
                        [{"text": "Регистрация"}],
                    ],
                    "resize_keyboard": True,
                    "one_time_keyboard": True
                })
            })
            user_state.state = None
            user_state.save()

        elif text == "Регистрация":
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Пожалуйста, отправьте ваш адрес корпоративной почты.",
                'reply_markup': json.dumps({"remove_keyboard": True})
            })
            user_state.state = 'waiting_for_email'
            user_state.save()

        elif user_state.state == 'waiting_for_email':
            if is_corporate_email(text):
                code = str(random.randint(100000, 999999))
                send_email.delay(text, code)  # Отправляем код на почту
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': f"Код подтверждения отправлен на {text}. Пожалуйста, введите его."
                })
                user_state.email = text
                user_state.confirmation_code = code
                user_state.state = 'waiting_for_code'
                user_state.save()
            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Пожалуйста, введите корректный адрес корпоративной почты."
                })

        elif user_state.state == 'waiting_for_code':
            if text == user_state.confirmation_code:
                user_state.state = "waiting_for_name"
                user_state.save()

                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Теперь введите Ваше имя.\nНапример: 'Петров Пётр Петрович' или 'Иван Иванов'",
                })

            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Код неверный. Попробуйте еще раз."
                })
        elif user_state.state == "waiting_for_name":
            if validate_name(text):
                user_state.state = ""
                user_state.is_registered = True
                user_state.name = text
                user_state.save()

                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Регистрация успешна!",
                })
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Теперь Вам необходимо загрузить договор с спортивной организацией и актуальный чек",
                    'reply_markup': get_main_keyboard(user_state)
                })
            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Введенное имя некорректно. Попробуйте еще раз.",
                })

        elif not user_state.is_registered:
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Вы не зарегистрированы"
            })
        elif text == "Узнать свой статус":
            today = timezone.now().date()
            first_day_of_current_month = today.replace(day=1)
            first_day_of_previous_month = (
                    first_day_of_current_month - datetime.timedelta(
                days=1)).replace(
                day=1)
            host_url = Settings.get_setting("HOST_URL",
                                            "http://localhost:8000")

            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': f"Ваше имя: {user_state.name}"
            })

            inline_keyboard = []

            user_contracts = Contract.objects.filter(user=user_state).order_by(
                "uploaded_at")
            latest_contract = user_contracts.last()

            user_cheques = Cheque.objects.filter(user=user_state).order_by(
                "uploaded_at"
            )
            latest_cheque = user_cheques.last()

            if latest_contract:
                inline_keyboard.append([{
                    "text": f"📥 Договор (загружен {latest_contract.uploaded_at.strftime('%d.%m.%Y')})",
                    "url": f'{host_url}{latest_contract.file.url}',
                }])
            else:
                inline_keyboard.append([{
                    "text": "Загрузить договор",
                }])

            if latest_cheque:
                inline_keyboard.append(
                    [{
                        "text": f"📥 Последний чек (загружен {latest_contract.uploaded_at.strftime('%d.%m.%Y')})",
                        "url": f'{host_url}{latest_cheque.file.url}',
                    }]
                )
            else:
                inline_keyboard.append({
                    "text": "Загрузить чек",
                })

            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': f"Документы, необходимые для компенсации",
                "reply_markup": {
                    "inline_keyboard": inline_keyboard
                }
            })

            required_count = int(
                Settings.get_setting("circle_required_count", "4"))
            user_circes_count = Circle.objects.filter(
                uploaded_at__gte=first_day_of_previous_month,
                user=user_state).count()
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': f"Кружки: {user_circes_count}/{required_count}",
            })
        elif text == "Загрузить договор":
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Отправьте PDF-файл с договором."
            })
            user_state.state = 'waiting_for_contract'
            user_state.save()

        elif text == "Загрузить чек":
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Отправьте PDF-файл с чеком."
            })
            user_state.state = 'waiting_for_receipt'
            user_state.save()

        elif text == "Изменить договор":
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Отправьте PDF-файл с договором."
            })
            user_state.state = 'waiting_for_contract'
            user_state.save()
        elif text.startswith("Загрузить чек"):
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Отправьте PDF-файл с чеком."
            })
            user_state.state = 'waiting_for_receipt'
            user_state.save()


        elif 'document' in message['message']:
            file_id = message['message']['document']['file_id']

            if user_state.state == 'waiting_for_contract':

                download_and_save_telegram_file(file_id, user_state,
                                                "contract")
                user_state.has_contract = True  # Обновляем флаг
                user_state.state = None
                user_state.save()

                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "✅ Договор успешно загружен!",
                    'reply_markup': get_main_keyboard(user_state)
                    # Обновляем кнопку
                })

            elif user_state.state == 'waiting_for_receipt':
                download_and_save_telegram_file(file_id, user_state, "receipt")
                user_state.state = None
                user_state.save()

                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "✅ Чек успешно загружен!",
                    'reply_markup': get_main_keyboard(user_state)
                })

        elif 'video_note' in message['message']:  # Обработка кружков
            now_date_minus_day = timezone.now() - datetime.timedelta(
                hours=24)
            file_id = message['message']['video_note']['file_id']
            user_today_circles = Circle.objects.filter(
                user=user_state,
                uploaded_at__gte=now_date_minus_day).order_by(
                "uploaded_at")
            if user_today_circles.exists():
                latest_circle_date = user_today_circles.last().uploaded_at
                wait_timedelta = calc_timedelta_between_dates(
                    now_date_minus_day, latest_circle_date)
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': f"Вы уже загружали кружок недавно. Подождите {wait_timedelta}"
                })
            else:
                download_and_save_telegram_file(file_id, user_state,
                                                "circle")
                save_circle(file_id,
                            chat_id)  # Функция для сохранения кружка
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Кружок получен и сохранен на сервере."
                })
            return HttpResponse('ok')

        else:
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Неизвестная команда."
            })

    return HttpResponse('ok')


def setwebhook(request):
    try:
        telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
        host_url = Settings.get_setting("HOST_URL") + '/getpost/'
        url = TELEGRAM_API_URL + telegram_token + "/setWebhook?url=" + host_url
        response = requests.post(url).json()
        return HttpResponse(f"{response}")
    except Exception as e:
        return HttpResponse(f"Not set: {str(e)}")


def handle_callback_query(message):
    callback_data = message["callback_query"]["data"]
    chat_id = message["callback_query"]["message"]["chat"]["id"]
    user = UserState.objects.get(chat_id=chat_id)

    # Add a debug log to inspect callback_data
    print(f"Callback Data: {callback_data}")
    if callback_data.startswith("success_report_"):
        obj_id = int(callback_data.replace("success_report_", ""))
        obj = Report.objects.filter(id=obj_id).first()
        obj.confirmed_by.add(user)
        obj.save()
        # Отправляем ответ пользователю
        send_message_to_user_generic({
            "chat_id": user.chat_id,
            "text": "✅ Вы успешно подтвердили получение отчета."
        })

    return HttpResponse('ok')
