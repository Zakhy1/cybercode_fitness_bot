from django.urls import path

from report.views import ReportView

app_name = 'report'

urlpatterns = [
    path('', ReportView.as_view(), name='report')
]
