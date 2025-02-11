import datetime
import json
import os
import re

import requests
from django.core.files.base import ContentFile
from django.http import HttpResponse

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.report import Report
from bot.models.user_state import UserState
from bot.tasks import send_message_to_user_generic
from settings.models import Settings
from project.settings import TELEGRAM_API_URL


def save_circle(file_id, chat_id):
    telegram_token = Settings.get_setting("TELEGRAM_TOKEN")
    url = TELEGRAM_API_URL + telegram_token + "/getFile"
    file_path = \
        requests.get(url, params={'file_id': file_id}).json()['result'][
            'file_path']
    download_url = f"{TELEGRAM_API_URL}{telegram_token}/{file_path}"

    # Скачивание и сохранение файла
    response = requests.get(download_url)
    path = f"media/videos/{chat_id}/"
    os.makedirs(path, exist_ok=True)
    with open(path + datetime.datetime.now().isoformat() + '.mp4', "wb") as f:
        f.write(response.content)


def download_and_save_telegram_file(file_id, user, model):
    """Скачивает файл с Telegram и сохраняет его в FileField модели,
    если это PDF или кружок размер не превышает сколько надо МБ."""

    token = Settings.get_setting("TELEGRAM_TOKEN")

    file_info_url = f"{TELEGRAM_API_URL}{token}/getFile?file_id={file_id}"
    response = requests.get(file_info_url).json()

    if "result" not in response:
        return "❌ Вы не отправили файл"

    file_path = response["result"]["file_path"]
    file_size = response["result"].get("file_size", 0)
    download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

    max_file_size_setting = int(Settings.get_setting("max_file_size", "20"))
    max_file_size = max_file_size_setting * 1024 * 1024
    if file_size > max_file_size:
        return (f"❌ Размер файла превышает {max_file_size}МБ. "
                f"Пожалуйста, загрузите файл меньшего размера.")

    filename = file_path.split("/")[-1]
    file_extension = os.path.splitext(filename)[-1].lower()

    file_data = requests.get(download_url).content

    if model == "circle":
        circle = Circle(user=user)
        circle.file.save(filename, ContentFile(file_data))
        circle.save()
        return circle.file.url

    if file_extension != '.pdf':
        return ("❌ Файл не является PDF. "
                "Пожалуйста, загрузите файл с расширением .pdf.")

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

    return "Неизвестная команда"


def get_main_keyboard(user_state):
    """Генерирует клавиатуру в зависимости от состояния пользователя."""
    if user_state.has_contract:
        contract_button = "Изменить договор"
    else:
        contract_button = "Загрузить договор"
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
    pattern = (r'^[А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)? [А-ЯЁ][а-яё]+(?:-[А-ЯЁ]['
               r'а-яё]+)?(?: [А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?)?$')
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
        return f"{int(years)} год" if years == 1 \
            else f"{int(years)} года" \
            if 2 <= years <= 4 else f"{int(years)} лет"
    elif months >= 1:
        return f"{int(months)} месяц" if months == 1 \
            else f"{int(months)} мес." \
            if 2 <= months <= 4 else f"{int(months)} месяцев"
    elif days >= 1:
        return f"{int(days)} день" if days == 1 \
            else f"{int(days)} дн." \
            if 2 <= days <= 4 else f"{int(days)} дней"
    elif hours >= 1:
        return f"{int(hours)} ч." if hours == 1 \
            else f"{int(hours)} ч." \
            if 2 <= hours <= 4 else f"{int(hours)} ч."
    elif minutes >= 1:
        return f"{int(minutes)} минута" if minutes == 1 \
            else f"{int(minutes)} мин." \
            if 2 <= minutes <= 4 else f"{int(minutes)} минут"
    else:
        return f"{int(seconds)} секунда" if seconds == 1 \
            else f"{int(seconds)} сек." \
            if 2 <= seconds <= 4 else f"{int(seconds)} секунд"


def handle_callback_query(message):
    callback_data = message["callback_query"]["data"]
    chat_id = message["callback_query"]["message"]["chat"]["id"]
    user = UserState.objects.get(chat_id=chat_id)

    if callback_data.startswith("success_report_"):
        obj_id = int(callback_data.replace("success_report_", ""))
        obj = Report.objects.filter(id=obj_id).first()
        obj.confirmed_by.add(user)
        obj.save()
        send_message_to_user_generic({
            "chat_id": user.chat_id,
            "text": "✅ Вы успешно подтвердили получение отчета."
        })

    return HttpResponse('ok')
