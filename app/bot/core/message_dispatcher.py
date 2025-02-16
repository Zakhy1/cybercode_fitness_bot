from bot.core.base import handle_callback_query
from bot.core.message_handler import TelegramBotHandler
from bot.tasks import send_message
from project.logging_settings import info_logger


class TelegramBotDispatcher:
    def dispatch(self, message):
        if "callback_query" in message:
            return handle_callback_query(message)

        handler = TelegramBotHandler(message)
        if handler.text == '/start':
            info_logger.info(f"Обработка /start\n{message}\n")
            handler.handle_start()
        elif handler.user_state.banned:
            info_logger.info(f"Забаненный пользователь стучится\n{message}\n")
            handler.handle_banned()
        elif handler.text == "Регистрация":
            info_logger.info(f"Регистрация\n{message}\n")
            handler.handle_registration()
        elif handler.user_state.state == 'waiting_for_email':
            info_logger.info(f"Ввод e-mail\n{message}\n")
            handler.handle_waiting_for_email()
        elif handler.user_state.state == 'waiting_for_code':
            info_logger.info(f"Ввод кода подтверждения\n{message}\n")
            handler.handle_waiting_for_code()
        elif handler.user_state.state == "waiting_for_name":
            info_logger.info(f"Ввод имени\n{message}\n")
            handler.handle_waiting_for_name()
        elif not handler.user_state.is_registered:
            info_logger.info(
                f"Не зарегистрированный чет пытается\n{message}\n")
            send_message("sendMessage", {
                'chat_id': handler.chat_id,
                'text': "Вы не зарегистрированы"
            })
        elif handler.text == "Узнать свой статус":
            info_logger.info(f"Запрос статуса\n{message}\n")
            handler.handle_status()
        elif handler.text in ["Загрузить договор", "Изменить договор"]:
            info_logger.info(f"Загрузка/изменение договора\n{message}\n")
            send_message("sendMessage", {
                'chat_id': handler.chat_id,
                'text': "Отправьте PDF-файл с договором.",
                'reply_markup': {
                    "keyboard": [
                        [{"text": "🔙 Отмена"}]
                    ],
                }
            })
            handler.user_state.state = 'waiting_for_contract'
            handler.user_state.save()
        elif handler.text.startswith("Загрузить чек"):
            info_logger.info(f"Загрузка чека\n{message}\n")
            send_message("sendMessage", {
                'chat_id': handler.chat_id,
                'text': "Отправьте PDF-файл с чеком.",
                'reply_markup': {
                    "keyboard": [
                        [{"text": "🔙 Отмена"}]
                    ],
                }
            })
            handler.user_state.state = 'waiting_for_receipt'
            handler.user_state.save()
        elif (
                handler.user_state.state == "waiting_for_contract" or handler.user_state.state == "waiting_for_receipt") and handler.text == "🔙 Отмена":
            info_logger.info(f"Возврат назад\n{message}\n")
            handler.handle_go_back()
        elif 'document' in message['message']:
            info_logger.info(f"Файл прилетел\n{message}\n")
            file_id = message['message']['document']['file_id']
            handler.handle_document(file_id)
        elif 'video_note' in message['message']:
            info_logger.info(f"Кружок прилетел\n{message}\n")
            file_id = message['message']['video_note']['file_id']
            handler.handle_video_note(file_id)
        else:
            info_logger.info(f"Неизвестная команда\n{message}\n")
            handler.handle_unknown_command()
