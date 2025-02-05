from django.contrib import admin

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState


@admin.register(UserState)
class UserStateAdmin(admin.ModelAdmin):
    pass


@admin.register(Cheque)
class ModelNameAdmin(admin.ModelAdmin):
    pass


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    pass


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    pass


