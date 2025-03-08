import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.generic import FormView, TemplateView, ListView

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState
from report.forms.form_report import ReportForm
from settings.models import Settings

months_names = {
    '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
    '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
    '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
}


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
        context['form'] = form
        return render(self.request, self.template_name, context)

    def generate_report(self, start_date, end_date):
        required_count = int(
            Settings.get_setting("circle_required_count", "4")
        )
        host_url = Settings.get_setting("HOST_URL", "http://localhost:8000")

        report = {"accessed": [], "not_accessed": []}
        months_names = {
            '01': 'январь', '02': 'февраль', '03': 'март', '04': 'апрель',
            '05': 'май', '06': 'июнь', '07': 'июль', '08': 'август',
            '09': 'сентябрь', '10': 'октябрь', '11': 'ноябрь', '12': 'декабрь'
        }

        users = UserState.objects.all()

        for user in users:
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
                uploaded_at__lte=end_date,
                user=user).count()
            if user_circles_count < required_count:
                report['not_accessed'].append({
                    "name": user.get_name(),
                    "reason": f"Количество посещений: {user_circles_count}/{required_count}"
                })
                continue

            # Получаем все чеки в диапазоне дат
            cheques = Cheque.objects.filter(
                user=user,
                uploaded_at__gte=start_date,
                uploaded_at__lte=end_date
            )

            if not cheques.exists():
                existent_cheque = Cheque.objects.filter(user=user).order_by(
                    "uploaded_at").last()
                if existent_cheque is not None:
                    report['not_accessed'].append({
                        "name": user.get_name(),
                        "reason": f"Нет чека за период: последний чек от "
                                  f"{existent_cheque.uploaded_at.strftime('%d.%m.%Y')}"
                    })
                else:
                    report['not_accessed'].append({
                        "name": user.get_name(),
                        "reason": "Нет чека за период"
                    })
                continue

            # Группируем чеки по месяцам, берем последний в каждом месяце
            cheques_by_month = {}
            for cheque in cheques:
                month_key = cheque.uploaded_at.strftime('%Y-%m')
                if month_key not in cheques_by_month or \
                        cheque.uploaded_at > cheques_by_month[
                    month_key].uploaded_at:
                    cheques_by_month[month_key] = cheque

            latest_contract = Contract.objects.filter(user=user).latest('uploaded_at')
            report["accessed"].append({
                "id": user.id,
                "name": user.get_name(),
                "visits_count": user_circles_count,
                "contract": f'{host_url}{latest_contract.file.url}',
                "cheques": [
                    {
                        "month": f"{months_names[cheque.uploaded_at.strftime('%m')]} "
                                 f"{cheque.uploaded_at.strftime('%Y')}",
                        "url": f'{host_url}{cheque.file.url}'
                    }
                    for cheque in cheques_by_month.values()
                ]
            })

        return report


class CircleHistoryView(ListView):
    template_name = "report/circle_history.html"
    model = Circle  # Указываем модель

    def get_queryset(self):
        date_start = self.request.GET.get("date_start")
        date_end = self.request.GET.get("date_end")
        user_id = self.kwargs.get('pk')

        # Исправленное условие
        if not date_start or not date_end or not user_id:
            return []

        try:
            start_date = datetime.datetime.strptime(date_start, "%d.%m.%Y")
            end_date = datetime.datetime.strptime(date_end, "%d.%m.%Y")
        except ValueError:
            return []

        circles_by_range = Circle.objects.filter(
            user_id=user_id,
            uploaded_at__gte=start_date,
            uploaded_at__lte=end_date
        )

        # Отладочный вывод
        return circles_by_range
