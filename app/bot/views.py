import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from settings.models import Settings
from bot.models import UserState  # Добавьте модель для отслеживания состояния пользователя

TELEGRAM_API_URL = "https://api.telegram.org/bot"


@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        message = json.loads(request.body.decode('utf-8'))
        chat_id = message['message']['chat']['id']
        text = message['message'].get('text', '')

        # Обработка команды /start
        if text == '/start':
            send_message("sendMessage", {
                'chat_id': chat_id,
                'text': "Привет! Пожалуйста, отправьте ваш адрес электронной почты."
            })
            # Сохранение состояния
            UserState.objects.update_or_create(
                chat_id=chat_id,
                defaults={'state': 'waiting_for_email'}
            )
        else:
            # Проверка состояния пользователя
            user_state = UserState.objects.filter(chat_id=chat_id).first()
            if user_state and user_state.state == 'waiting_for_email':
                # Здесь можно добавить валидацию email
                if "@" in text:
                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': f"Спасибо! Ваш email: {text} сохранен."
                    })
                    user_state.state = None  # Сброс состояния
                    user_state.save()
                else:
                    send_message("sendMessage", {
                        'chat_id': chat_id,
                        'text': "Пожалуйста, введите корректный адрес электронной почты."
                    })
            else:
                send_message("sendMessage", {
                    'chat_id': chat_id,
                    'text': f"Ваше сообщение: {text}"
                })
    return HttpResponse('ok')


def send_message(method, data):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + '/' + method
    response = requests.post(url, data=data)
    return response


def setwebhook(request):
    try:
        telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
        host_url = Settings.get_setting("HOST_URL") + '/getpost/'
        url = TELEGRAM_API_URL + telegram_token + "/setWebhook?url=" + host_url
        response = requests.post(url).json()
        return HttpResponse(f"{response}")
    except Exception as e:
        return HttpResponse(f"Not set: {str(e)}")
