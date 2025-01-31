import datetime
import json
import os
import random
import smtplib
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from settings.models import Settings
from bot.models import UserState
import requests
from django.core.mail import send_mail

TELEGRAM_API_URL = "https://api.telegram.org/bot"


@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        message = json.loads(request.body.decode('utf-8'))
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
                        [{"text": "Подтвердить получение сообщений"}]
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
                'text': "Пожалуйста, отправьте ваш адрес электронной почты."
            })
            user_state.state = 'waiting_for_email'
            user_state.save()

        elif user_state.state == 'waiting_for_email':
            if "@" in text:  # Простая проверка email
                code = str(random.randint(100000, 999999))
                send_email(text, code)  # Отправляем код на почту
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
                    'text': "Пожалуйста, введите корректный адрес электронной почты."
                })

        elif user_state.state == 'waiting_for_code':
            if text == user_state.confirmation_code:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Регистрация успешна! Теперь вы можете получать сообщения."
                })
                user_state.is_registered = True
                user_state.state = None
                user_state.save()
            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Код неверный. Попробуйте еще раз."
                })

        elif text == "Подтвердить получение сообщений":
            if user_state.is_registered:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Вы подтверждаете получение регулярных сообщений?",
                    'reply_markup': json.dumps({
                        "keyboard": [
                            [{"text": "Да"}],
                            [{"text": "Нет"}]
                        ],
                        "resize_keyboard": True,
                        "one_time_keyboard": True
                    })
                })
                user_state.state = 'confirm_notifications'
                user_state.save()
            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Сначала пройдите регистрацию."
                })

        elif user_state.state == 'confirm_notifications':
            if text == "Да":
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Вы будете получать регулярные сообщения."
                })
                user_state.receive_notifications = True
                user_state.state = None
                user_state.save()
            elif text == "Нет":
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': "Вы отказались от получения сообщений."
                })
                user_state.receive_notifications = False
                user_state.state = None
                user_state.save()

        elif 'video_note' in message['message']:  # Обработка кружков
            file_id = message['message']['video_note']['file_id']
            save_circle(file_id, chat_id)  # Функция для сохранения кружка
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Кружок получен и сохранен на сервере."
            })

    return HttpResponse('ok')


def send_message(method, data):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + '/' + method
    response = requests.post(url, json=data)
    return response


def send_email(email, code):
    subject = "Код подтверждения для регистрации"
    message = f"Ваш код подтверждения: {code}"
    from_email = Settings.get_setting("EMAIL_HOST_USER")  # Если храните email в настройках
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        print(f"Код отправлен на {email}")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")


def save_circle(file_id, chat_id):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + "/getFile"
    file_path = requests.get(url, params={'file_id': file_id}).json()['result']['file_path']
    download_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"

    # Скачивание и сохранение файла
    response = requests.get(download_url)
    path = f"media/videos/{chat_id}/"
    os.makedirs(path, exist_ok=True)
    with open(path + datetime.datetime.now().isoformat() + '.mp4', "wb") as f:
        f.write(response.content)

def setwebhook(request):
    try:
        telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
        host_url = Settings.get_setting("HOST_URL") + '/getpost/'
        url = TELEGRAM_API_URL + telegram_token + "/setWebhook?url=" + host_url
        response = requests.post(url).json()
        return HttpResponse(f"{response}")
    except Exception as e:
        return HttpResponse(f"Not set: {str(e)}")