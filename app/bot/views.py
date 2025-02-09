import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from project.settings import TELEGRAM_API_URL
from project.logging_settings import error_logger, info_logger

from settings.models import Settings

from bot.core.base import handle_callback_query
from bot.core.main import TelegramBotHandler
from bot.tasks import send_message
from bot.util.base_view import base_view

import requests


@base_view
@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        try:
            message = json.loads(request.body.decode('utf-8'))
            if "callback_query" in message:
                return handle_callback_query(message)

            handler = TelegramBotHandler(message)

            if handler.text == '/start':
                handler.handle_start()
            elif handler.text == "Регистрация":
                handler.handle_registration()
            elif handler.user_state.state == 'waiting_for_email':
                handler.handle_waiting_for_email()
            elif handler.user_state.state == 'waiting_for_code':
                handler.handle_waiting_for_code()
            elif handler.user_state.state == "waiting_for_name":
                handler.handle_waiting_for_name()
            elif not handler.user_state.is_registered:
                send_message("sendMessage", {
                    'chat_id': handler.chat_id,
                    'text': "Вы не зарегистрированы"
                })
            elif handler.text == "Узнать свой статус":
                handler.handle_status()
            elif handler.text in ["Загрузить договор", "Изменить договор"]:
                send_message("sendMessage", {
                    'chat_id': handler.chat_id,
                    'text': "Отправьте PDF-файл с договором."
                })
                handler.user_state.state = 'waiting_for_contract'
                handler.user_state.save()
            elif handler.text.startswith("Загрузить чек"):
                send_message("sendMessage", {
                    'chat_id': handler.chat_id,
                    'text': "Отправьте PDF-файл с чеком."
                })
                handler.user_state.state = 'waiting_for_receipt'
                handler.user_state.save()
            elif 'document' in message['message']:
                file_id = message['message']['document']['file_id']
                handler.handle_document(file_id)
            elif 'video_note' in message['message']:
                file_id = message['message']['video_note']['file_id']
                handler.handle_video_note(file_id)
            else:
                handler.handle_unknown_command()

        except Exception as e:
            error_logger.error(f"Error handling message: {e}")
            return HttpResponse('error', status=500)

    return HttpResponse('ok')


def setwebhook(request):
    try:
        telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
        host_url = Settings.get_setting("HOST_URL") + '/getpost/'
        url = TELEGRAM_API_URL + telegram_token + "/setWebhook?url=" + host_url
        response = requests.post(url).json()
        info_logger.info(f"Установка токен({telegram_token})")
        info_logger.info(f"Установка webhook на url ({url})")
        info_logger.info(f"{response}")
        return HttpResponse(f"{response}")
    except Exception as e:
        return HttpResponse(f"Not set: {str(e)}")
