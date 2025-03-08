from django.urls import path

from report.views import ReportView, CircleHistoryView

app_name = 'report'

urlpatterns = [
    path('', ReportView.as_view(), name='report'),
    path('circle_history/<int:pk>/', CircleHistoryView.as_view(), name='circle_history')
]
