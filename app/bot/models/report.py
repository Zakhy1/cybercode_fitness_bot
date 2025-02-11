import datetime
from datetime import timedelta

from django.db import models
from django.utils.timezone import now

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState
from settings.models import Settings


class Report(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата конца")
    report_data = models.JSONField(verbose_name="Содержимое")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлен")
    confirmed_by = models.ManyToManyField(UserState, blank=True, verbose_name="Подтвержден")

    def __str__(self):
        return f"Report {self.start_date} - {self.end_date}"

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"

    def send_report(self):
        from bot.tasks import send_message_to_user_generic

        """Отправка отчета"""
        users_to_send = UserState.objects.filter(send_reports=True)
        send_not_accessed = bool(
            int(Settings.get_setting("send_not_accessed", "1")))
        for user in users_to_send:
            send_message_to_user_generic({
                "chat_id": user.chat_id,
                "text": f"Отчет от {self.start_date.strftime('%d.%m.%Y')} по {self.end_date.strftime('%d.%m.%Y')}"
            })
            if send_not_accessed:
                if len(self.report_data['not_accessed']) > 0:
                    send_message_to_user_generic({
                        "chat_id": user.chat_id,
                        "text": f"❌ Не подходят под условия компенсации"
                    })
                for row in self.report_data['not_accessed']:
                    row['chat_id'] = user.chat_id
                    send_message_to_user_generic(row)
                send_message_to_user_generic({
                    "chat_id": user.chat_id,
                    "text": f"✅ Подходят под условия компенсации"
                })
            for row in self.report_data['accessed']:
                row['chat_id'] = user.chat_id
                send_message_to_user_generic(row)
            send_message_to_user_generic({
                "chat_id": user.chat_id,
                "text": "Пожалуйста, подтвердите ознакомление с отчетом",
                "reply_markup": {
                    "inline_keyboard": [
                        [{
                            "text": "Подтвердить получение отчета",
                            "callback_data": f"success_report_{self.id}"
                        }],
                    ]
                }
            })
        self.is_sent = True
        self.save()

    def confirm_report(self, user):
        """Подтверждение прочтения отчета пользователем"""
        self.confirmed_by.add(user)
        self.save()

    @classmethod
    def create_and_send(cls, save_to_db=True):
        """Создает и отправляет отчет, можно без сохранения в БД"""
        report_data, start_date, end_date = cls.make_report()
        report = cls.objects.create(
            start_date=start_date,
            end_date=end_date,
            report_data=report_data,
        )
        report.send_report()
        if save_to_db:
            report.save()
        return report

    @staticmethod
    def make_report():
        # Создание тела отчета
        today = now().date()
        first_day_of_current_month = today.replace(day=1)
        first_day_of_previous_month = (
                first_day_of_current_month - timedelta(days=1)).replace(day=1)
        end_date = datetime.datetime.now().date()
        required_count = int(
            Settings.get_setting("circle_required_count", "4"))
        host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")

        report = {"accessed": [], "not_accessed": []}

        users = UserState.objects.all()

        for user in users:
            # Отсеиваем
            if not user.is_registered:
                report['not_accessed'].append({
                    "chat_id": "",
                    "text": f" {user.name} - ❌ (Не зарегистрирован)"
                })
                continue
            if not user.has_contract:
                report['not_accessed'].append({
                    "chat_id": "",
                    "text": f" {user.name} - ❌ (Не отправил договор)"
                })
                continue
            user_circes_count = Circle.objects.filter(
                uploaded_at__gte=first_day_of_previous_month,
                user=user).count()
            if user_circes_count < required_count:
                report['not_accessed'].append({
                    "chat_id": "",
                    "text": f" {user.name} - ❌ (Количество кружков: {user_circes_count}, а необходимо: {required_count})"
                })
                continue
            try:
                latest_cheque = Cheque.objects.filter(
                    uploaded_at__gte=first_day_of_previous_month,
                    user=user).latest("uploaded_at")
            except Cheque.DoesNotExist:
                existent_cheque = Cheque.objects.filter(user=user).order_by(
                    "uploaded_at").last()
                if existent_cheque is not None:
                    report['not_accessed'].append({
                        "chat_id": "",
                        "text": f"{user.name} - ❌ (Нет чека за месяц: последний от {existent_cheque.uploaded_at})"
                    })
                else:
                    report['not_accessed'].append({
                        "chat_id": "",
                        "text": f"{user.name} - ❌ (Нет чека за месяц)"
                    })
                continue
            # Добавляем в отчет
            latest_contract = Contract.objects.latest('uploaded_at')
            report["accessed"].append({
                "chat_id": "",
                "text": f"✅ {user.get_name()}",
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

        return report, first_day_of_previous_month, end_date
