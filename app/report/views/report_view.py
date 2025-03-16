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
from report.service import ReportService
from settings.models import Settings


class ReportView(LoginRequiredMixin, FormView):
    def __init__(self):
        super().__init__()
        self.service = ReportService()

    template_name = 'report/report.html'
    form_class = ReportForm

    def form_valid(self, form):
        required_count = int(
            Settings.get_setting("circle_required_count", "4")
        )
        date_start = form.cleaned_data['date_start']
        date_end = form.cleaned_data['date_end']

        report_data = self.service.generate_report(date_start, date_end)

        context = self.get_context_data()
        context['report_data'] = report_data
        context['date_start'] = date_start.strftime("%d.%m.%Y")
        context['date_end'] = date_end.strftime("%d.%m.%Y")
        context["required_count"] = required_count
        context['form'] = form
        return render(self.request, self.template_name, context)
