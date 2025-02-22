from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from report.forms.form_report import ReportForm


class ReportView(LoginRequiredMixin, FormView):
    template_name = 'report/report.html'
    form_class = ReportForm
    success_url = '/'

    def form_valid(self, form):
        return super().form_valid(form)
