import datetime
import json
import random
import logging

from bot.core.base import save_circle, download_and_save_telegram_file, \
    get_main_keyboard, validate_name, \
    is_corporate_email, calc_timedelta_between_dates
from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.report import Report
from bot.models.user_state import UserState
from bot.tasks import send_email, send_message_to_user_generic, send_message
from project.settings import TELEGRAM_API_URL
from settings.models import Settings
import requests
from django.utils import timezone


class TelegramBotHandler:
    def __init__(self, message):
        self.message = message
        self.chat_id = message['message']['chat']['id']
        self.text = message['message'].get('text', '')
        self.user_state, _ = UserState.objects.get_or_create(
            chat_id=self.chat_id)

    def handle_start(self):
        send_message("sendMessage", {
            'chat_id': self.chat_id,
            'text': "Добро пожаловать! Пожалуйста, выберите действие:",
            'reply_markup': json.dumps({
                "keyboard": [
                    [{"text": "Регистрация"}],
                ],
                "resize_keyboard": True,
                "one_time_keyboard": True
            })
        })
        self.user_state.state = None
        self.user_state.save()

    def handle_registration(self):
        send_message("sendMessage", {
            'chat_id': self.chat_id,
            'text': "Пожалуйста, отправьте ваш адрес корпоративной почты.",
            'reply_markup': json.dumps({"remove_keyboard": True})
        })
        self.user_state.state = 'waiting_for_email'
        self.user_state.save()

    def handle_waiting_for_email(self):
        if is_corporate_email(self.text):
            code = str(random.randint(100000, 999999))
            send_email.delay(self.text, code)  # Отправляем код на почту
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': f"Код подтверждения отправлен на {self.text}. Пожалуйста, введите его."
            })
            self.user_state.email = self.text
            self.user_state.confirmation_code = code
            self.user_state.state = 'waiting_for_code'
            self.user_state.save()
        else:
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Пожалуйста, введите корректный адрес корпоративной почты."
            })

    def handle_waiting_for_code(self):
        if self.text == self.user_state.confirmation_code:
            self.user_state.state = "waiting_for_name"
            self.user_state.save()

            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Теперь введите Ваше имя.\nНапример: 'Петров Пётр Петрович' или 'Иван Иванов'",
            })
        else:
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Код неверный. Попробуйте еще раз."
            })

    def handle_waiting_for_name(self):
        if validate_name(self.text):
            self.user_state.state = ""
            self.user_state.is_registered = True
            self.user_state.name = self.text
            self.user_state.save()

            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Регистрация успешна!",
            })
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Теперь Вам необходимо загрузить договор с спортивной организацией и актуальный чек",
                'reply_markup': get_main_keyboard(self.user_state)
            })
        else:
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Введенное имя некорректно. Попробуйте еще раз.",
            })

    def handle_status(self):
        today = timezone.now().date()
        first_day_of_current_month = today.replace(day=1)
        first_day_of_previous_month = (
                first_day_of_current_month - datetime.timedelta(
            days=1)).replace(day=1)
        host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")

        send_message("sendMessage", {
            'chat_id': self.chat_id,
            'text': f"Ваше имя: {self.user_state.name}"
        })

        inline_keyboard = []

        user_contracts = Contract.objects.filter(
            user=self.user_state).order_by(
            "uploaded_at")
        latest_contract = user_contracts.last()

        user_cheques = Cheque.objects.filter(user=self.user_state).order_by(
            "uploaded_at"
        )
        latest_cheque = user_cheques.last()

        if latest_contract:
            inline_keyboard.append([{
                "text": f"📥 Договор (загружен {latest_contract.uploaded_at.strftime('%d.%m.%Y')})",
                "url": f'{host_url}{latest_contract.file.url}',
            }])
        else:
            inline_keyboard.append([{
                "text": "Загрузить договор",
            }])

        if latest_cheque:
            inline_keyboard.append(
                [{
                    "text": f"📥 Последний чек (загружен {latest_contract.uploaded_at.strftime('%d.%m.%Y')})",
                    "url": f'{host_url}{latest_cheque.file.url}',
                }]
            )
        else:
            inline_keyboard.append({
                "text": "Загрузить чек",
            })

        send_message("sendMessage", {
            'chat_id': self.chat_id,
            'text': f"Документы, необходимые для компенсации",
            "reply_markup": {
                "inline_keyboard": inline_keyboard
            }
        })

        required_count = int(
            Settings.get_setting("circle_required_count", "4"))
        user_circes_count = Circle.objects.filter(
            uploaded_at__gte=first_day_of_previous_month,
            user=self.user_state).count()
        send_message("sendMessage", {
            'chat_id': self.chat_id,
            'text': f"Кружки: {user_circes_count}/{required_count}",
        })

    def handle_document(self, file_id):
        if self.user_state.state == 'waiting_for_contract':
            download_and_save_telegram_file(file_id, self.user_state,
                                            "contract")
            self.user_state.has_contract = True
            self.user_state.state = None
            self.user_state.save()

            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "✅ Договор успешно загружен!",
                'reply_markup': get_main_keyboard(self.user_state)
            })

        elif self.user_state.state == 'waiting_for_receipt':
            download_and_save_telegram_file(file_id, self.user_state,
                                            "receipt")
            self.user_state.state = None
            self.user_state.save()

            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "✅ Чек успешно загружен!",
                'reply_markup': get_main_keyboard(self.user_state)
            })

    def handle_video_note(self, file_id):
        now_date_minus_day = timezone.now() - datetime.timedelta(hours=24)
        user_today_circles = Circle.objects.filter(
            user=self.user_state,
            uploaded_at__gte=now_date_minus_day).order_by("uploaded_at")
        if user_today_circles.exists():
            latest_circle_date = user_today_circles.last().uploaded_at
            wait_timedelta = calc_timedelta_between_dates(
                latest_circle_date, now_date_minus_day)
            print(f"now_date_minus_day {now_date_minus_day}")
            print(f"latest_circle_date {latest_circle_date}")
            print(wait_timedelta)
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': f"Вы уже загружали кружок недавно. Подождите {wait_timedelta}"
            })
        else:
            download_and_save_telegram_file(file_id, self.user_state, "circle")
            save_circle(file_id, self.chat_id)
            send_message("sendMessage", {
                'chat_id': self.chat_id,
                'text': "Кружок получен и сохранен на сервере."
            })

    def handle_unknown_command(self):
        send_message("sendMessage", {
            'chat_id': self.chat_id,
            'text': "Неизвестная команда."
        })
