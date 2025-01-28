import json
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from project.settings import TELEGRAM_API_URL, URL


@csrf_exempt
def telegram_bot(request):
    if request.method == 'POST':
        message = json.loads(request.body.decode('utf-8'))
        chat_id = message['message']['chat']['id']
        text = message['message']['text']
        send_message("sendMessage", {
            'chat_id': f'your message {text}'
        })
    return HttpResponse('ok')


def send_message(method, data):
    return requests.post(TELEGRAM_API_URL + method, data)

def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  return HttpResponse(f"{response}")