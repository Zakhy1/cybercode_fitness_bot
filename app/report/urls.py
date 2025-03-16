from django.urls import path

from report.views.circle_history_view import CircleHistoryView
from report.views.report_view import ReportView

app_name = 'report'

urlpatterns = [
    path('', ReportView.as_view(),
         name='report'),
    path('circle_history/<int:pk>/', CircleHistoryView.as_view(),
         name='circle_history')
]
