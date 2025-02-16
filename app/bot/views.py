import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from bot.core.message_dispatcher import TelegramBotDispatcher
from project.settings import TELEGRAM_API_URL
from project.logging_settings import error_logger, info_logger

from settings.models import Settings

from bot.core.base import handle_callback_query
from bot.core.message_handler import TelegramBotHandler
from bot.tasks import send_message
from bot.util.base_view import base_view

import requests


@base_view
@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        message = {}
        try:
            message = json.loads(request.body.decode('utf-8'))
            dispatcher = TelegramBotDispatcher()
            dispatcher.dispatch(message)
        except Exception as e:
            error_logger.error(f"Ошибка во время обработки сообщения: {e}\n\n "
                               f"Сообщение: {message}\n")
            return HttpResponse('error', status=500)

    return HttpResponse('ok')


def setwebhook(request):
    try:
        telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
        host_url = Settings.get_setting("HOST_URL") + '/getpost/'
        url = TELEGRAM_API_URL + telegram_token + "/setWebhook?url=" + host_url
        response = requests.post(url).json()
        info_logger.info(f"Установка webhook на url ({url})")
        info_logger.info(f"{response}")
        return HttpResponse(f"{response}")
    except Exception as e:
        return HttpResponse(f"Not set: {str(e)}")
