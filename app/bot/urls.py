from django.urls import path
from . import views

urlpatterns = [
    path('getpost/', views.TelegramBotWebhookView.as_view(),
         name='telegram_bot'),
    path('setwebhook/', views.TelegramBotSetwebhookView.as_view(),
         name='setwebhook')
]
