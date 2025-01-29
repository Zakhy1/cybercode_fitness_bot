from django.contrib import admin

from bot.models import UserState


@admin.register(UserState)
class UserStateAdmin(admin.ModelAdmin):
    pass
