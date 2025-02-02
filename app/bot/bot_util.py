import datetime
import json
import os

import requests
from django.core.files.base import ContentFile

from bot.models.cheque import Cheque
from bot.models.contract import Contract
from settings.models import Settings
from project.settings import TELEGRAM_API_URL


def send_message(method, data):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + '/' + method
    response = requests.post(url, json=data)
    return response


def save_circle(file_id, chat_id):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + "/getFile"
    file_path = \
        requests.get(url, params={'file_id': file_id}).json()['result'][
            'file_path']
    download_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"

    # Скачивание и сохранение файла
    response = requests.get(download_url)
    path = f"media/videos/{chat_id}/"
    os.makedirs(path, exist_ok=True)
    with open(path + datetime.datetime.now().isoformat() + '.mp4', "wb") as f:
        f.write(response.content)


# def set_bot_commands():
#     telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
#     url = TELEGRAM_API_URL + telegram_token + "/setMyCommands"
#     commands = [
#         {"command": "add_cheque", "description": "🧾 Добавить чек"},
#         {"command": "contract", "description": "📄 Добавить договор"},
#     ]
#     response = requests.post(url, json={"commands": commands})
#     return response.json()


def download_and_save_telegram_file(file_id, user, model):
    """Скачивает файл с Telegram и сохраняет его в FileField модели."""

    token = Settings.get_setting("TELEGRAM_TOKEN")

    # Получаем путь к файлу на серверах Telegram
    file_info_url = f"{TELEGRAM_API_URL}{token}/getFile?file_id={file_id}"
    response = requests.get(file_info_url).json()

    if "result" not in response:
        return None

    file_path = response["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

    # Скачиваем файл
    file_data = requests.get(download_url).content
    filename = file_path.split("/")[-1]  # Получаем имя файла

    # Определяем, какую модель использовать (Contract или Receipt)
    if model == "contract":
        contract = Contract(user=user)
        contract.file.save(filename,
                           ContentFile(file_data))  # Сохраняем в FileField
        contract.save()
        return contract.file.url

    elif model == "receipt":
        receipt = Cheque(user=user)
        receipt.file.save(filename, ContentFile(file_data))
        receipt.save()
        return receipt.file.url

    return None


def get_main_keyboard(user_state):
    """Генерирует клавиатуру в зависимости от состояния пользователя."""
    contract_button = "Изменить договор" if user_state.has_contract else "Загрузить договор"
    try:
        latest_cheque = Cheque.objects.filter(user=user_state).latest(
            "uploaded_at")
        latest_cheque_date = latest_cheque.uploaded_at.strftime("%d.%m.%Y")
        cheque_button = f"Загрузить чек (Загружен {latest_cheque_date})"
    except Cheque.DoesNotExist:
        cheque_button = "Загрузить чек"
    return json.dumps({
        "keyboard": [
            [{"text": contract_button}],
            [{"text": cheque_button}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    })
