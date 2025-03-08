import json

from django.http import HttpResponse
from django.views.generic import View

from bot.core.message_dispatcher import TelegramBotDispatcher
from bot.util.csrf_exempt_mixin import CSRFExemptMixin
from project.settings import TELEGRAM_API_URL
from project.logging_settings import error_logger, info_logger

from settings.models import Settings

import requests


class TelegramBotWebhookView(CSRFExemptMixin, View):
    def post(self, request):
        message = {}
        try:
            message = json.loads(request.body.decode('utf-8'))
            dispatcher = TelegramBotDispatcher()
            dispatcher.dispatch(message)
            return HttpResponse('ok')
        except Exception as e:
            error_logger.error(
                f"Ошибка во время обработки сообщения: {e}\nСообщение: {message}\n")
            return HttpResponse('error', status=500)



class TelegramBotSetwebhookView(View):
    def get(self, request):
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
