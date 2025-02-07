import json
import random
import traceback

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from bot.bot_util import send_message, save_circle, \
    download_and_save_telegram_file, get_main_keyboard, validate_name, \
    is_corporate_email
from bot.models.report import Report
from bot.models.user_state import UserState
from bot.tasks import send_email, send_message_to_user_generic
from project.settings import TELEGRAM_API_URL
from settings.models import Settings
import requests


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
                    'text': "Теперь введите Ваше имя.\nНапример: 'Пётр Петрович Петров' или 'Иван Иванов'",
                    'reply_markup': get_main_keyboard(user_state)
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
                    'reply_markup': get_main_keyboard(user_state)
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
                    'reply_markup': get_main_keyboard(user_state)
                })
        elif 'video_note' in message['message']:  # Обработка кружков
            if user_state.is_registered:
                file_id = message['message']['video_note']['file_id']
                download_and_save_telegram_file(file_id, user_state,
                                                "circle")
                save_circle(file_id, chat_id)  # Функция для сохранения кружка
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Кружок получен и сохранен на сервере."
                })
            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Вы не зарегистрированы, чтобы отправлять кружки!"
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
