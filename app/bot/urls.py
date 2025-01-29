from django.urls import path
from . import views
from .views import setwebhook

urlpatterns = [
    path('getpost/', views.telegram_bot, name='telegram_bot'),
    path('setwebhook/', views.setwebhook, name='setwebhook'),  # new
]
