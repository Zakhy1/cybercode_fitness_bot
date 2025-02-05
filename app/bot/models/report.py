from datetime import timedelta

from django.db import models
from django.utils.timezone import now

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState
from settings.models import Settings


class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    report_data = models.JSONField()
    is_sent = models.BooleanField(default=False)
    confirmed_by = models.ManyToManyField(UserState, blank=True)

    def __str__(self):
        return f"Report {self.start_date} - {self.end_date}"

    def generate_report(self):
        """Генерация отчета"""
        today = now().date()
        first_day_of_current_month = today.replace(day=1)
        first_day_of_previous_month = (
                first_day_of_current_month - timedelta(days=1)).replace(day=1)

        start_str = first_day_of_previous_month.strftime("%d.%m.%Y")
        required_count = int(Settings.get_setting("circle_required_count", "4"))
        host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")


        admin_chat_id = int(Settings.get_setting("admin_chat_id", "389838514"))
        report = [{
                "chat_id": admin_chat_id,
                "text": f"Отчет от {start_str}",
            }]

        users = UserState.objects.all()

        for user in users:
            if not user.is_registered or not user.has_contract:
                continue

            user_circes_count = Circle.objects.filter(
                uploaded_at__gte=first_day_of_previous_month,
                user=user).count()
            if user_circes_count < required_count:
                continue

            try:
                latest_cheque = Cheque.objects.filter(
                    uploaded_at__gte=first_day_of_previous_month,
                    user=user).latest("uploaded_at")
            except Cheque.DoesNotExist:
                continue

            latest_contract = Contract.objects.latest('uploaded_at')

            report.append({
                "chat_id": admin_chat_id,
                "text": user.get_name(),
                "disable_notification": True,
                "reply_markup": {
                    "inline_keyboard": [
                        [{
                            "text": "📥 Договор",
                            "url": f'{host_url}{latest_contract.file.url}',
                        }],
                        [{
                            "text": "📥 Последний чек",
                            "url": f'{host_url}{latest_cheque.file.url}',
                        }]
                    ]
                }
            })
        # Отдельное сообщение с кнопкой подтверждения
        report.append({
            "chat_id": admin_chat_id,
            "text": "🔔 Пожалуйста, подтвердите получение отчета:",
            "reply_markup": {
                "inline_keyboard": [
                    [{
                        "text": "✅ Подтвердить получение",
                        "callback_data": f"confirm_report_{self.id}"
                    }]
                ]
            }
        })

        self.start_date = first_day_of_previous_month
        self.end_date = today
        self.report_data = report

    def send_report(self):
        from bot.tasks import send_message_to_user_generic

        """Отправка отчета"""
        for row in self.report_data:
            send_message_to_user_generic.delay(row)
        self.is_sent = True
        self.save()

    def confirm_report(self, user):
        """Подтверждение прочтения отчета пользователем"""
        self.confirmed_by.add(user)
        self.save()

    @classmethod
    def create_and_send(cls, save_to_db=True):
        """Создает и отправляет отчет, можно без сохранения в БД"""
        report = cls()
        report.generate_report()
        report.send_report()
        if save_to_db:
            report.save()
        return report

