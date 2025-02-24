from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import FormView

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState
from report.forms.form_report import ReportForm
from settings.models import Settings


class ReportView(LoginRequiredMixin, FormView):
    template_name = 'report/report.html'
    form_class = ReportForm

    def form_valid(self, form):
        required_count = int(
            Settings.get_setting("circle_required_count", "4")
        )
        date_start = form.cleaned_data['date_start']
        date_end = form.cleaned_data['date_end']

        report_data = self.generate_report(date_start, date_end)

        context = self.get_context_data()
        context['report_data'] = report_data
        context['date_start'] = date_start.strftime("%d.%m.%Y")
        context['date_end'] = date_end.strftime("%d.%m.%Y")
        context["required_count"] = required_count
        # Передаем форму обратно для повторного заполнения
        context['form'] = form
        return render(self.request, self.template_name, context)

    def generate_report(self, start_date, end_date):
        required_count = int(
            Settings.get_setting("circle_required_count", "4")
        )
        host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")

        report = {"accessed": [], "not_accessed": []}

        users = UserState.objects.all()

        for user in users:
            # Отсеиваем
            if not user.is_registered:
                if user.name is None:
                    continue
                report['not_accessed'].append({
                    "name": user.get_name(),
                    "reason": "Не зарегистрирован"
                })
                continue

            user_has_contract = Contract.objects.filter(user=user).exists()

            if not user_has_contract:
                report['not_accessed'].append({
                    "name": user.get_name(),
                    "reason": "Не отправил договор"
                })
                continue
            user_circles_count = Circle.objects.filter(
                uploaded_at__gte=start_date,
                user=user).count()
            if user_circles_count < required_count:
                report['not_accessed'].append({
                    "name": user.get_name(),
                    "reason":
                        f"Количество посещений: {user_circles_count}/{required_count}"
                })
                continue
            try:
                latest_cheque = Cheque.objects.filter(
                    uploaded_at__gte=start_date,
                    user=user).latest("uploaded_at")
            except Cheque.DoesNotExist:
                existent_cheque = Cheque.objects.filter(user=user).order_by(
                    "uploaded_at").last()
                if existent_cheque is not None:
                    report['not_accessed'].append({
                        "name": user.get_name(),
                        "reason":
                            f"Нет чека за месяц: последний чек"
                            f"от {existent_cheque.uploaded_at.strftime("%d.%m.%Y")})"
                    })
                else:
                    report['not_accessed'].append({
                        "reason": user.get_name(),
                        "text": "Нет чека за месяц"
                    })
                continue
            # Добавляем в отчет
            latest_contract = Contract.objects.latest('uploaded_at')
            report["accessed"].append({
                "name": user.get_name(),
                "visits_count": user_circles_count,
                "contract": f'{host_url}{latest_contract.file.url}',
                "cheque": f'{host_url}{latest_cheque.file.url}'
            })
        return report
