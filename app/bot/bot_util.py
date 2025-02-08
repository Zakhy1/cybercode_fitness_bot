import datetime
import json
import os
import re

import requests
from django.core.files.base import ContentFile

from bot.models.cheque import Cheque
from bot.models.circle import Circle
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

    elif model == "circle":
        circle = Circle(user=user)
        circle.file.save(filename, ContentFile(file_data))
        circle.save()
        return circle.file.url

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
            [{"text": cheque_button}],
            [{"text": "Узнать свой статус"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    })


def validate_name(name):
    pattern = r'^[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)? [А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?(?: [А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?)?$'
    return bool(re.fullmatch(pattern, name)) and len(name) <= 254


def is_corporate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@cybercode\.pro$'
    return bool(re.fullmatch(pattern, email))


def calc_timedelta_between_dates(date_1, date_2) -> str:
    delta = date_1 - date_2

    seconds = delta.total_seconds()
    years, remainder = divmod(seconds, 60 * 60 * 24 * 365)
    months, remainder = divmod(remainder, 60 * 60 * 24 * 30)
    days, remainder = divmod(remainder, 60 * 60 * 24)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)

    if years >= 1:
        return f"{int(years)} год" if years == 1 else f"{int(years)} года" if 2 <= years <= 4 else f"{int(years)} лет"
    elif months >= 1:
        return f"{int(months)} месяц" if months == 1 else f"{int(months)} мес." if 2 <= months <= 4 else f"{int(months)} месяцев"
    elif days >= 1:
        return f"{int(days)} день" if days == 1 else f"{int(days)} дн." if 2 <= days <= 4 else f"{int(days)} дней"
    elif hours >= 1:
        return f"{int(hours)} час" if hours == 1 else f"{int(hours)} ч." if 2 <= hours <= 4 else f"{int(hours)} часов"
    elif minutes >= 1:
        return f"{int(minutes)} минута" if minutes == 1 else f"{int(minutes)} мин." if 2 <= minutes <= 4 else f"{int(minutes)} минут"
    else:
        return f"{int(seconds)} секунда" if seconds == 1 else f"{int(seconds)} сек." if 2 <= seconds <= 4 else f"{int(seconds)} секунд"