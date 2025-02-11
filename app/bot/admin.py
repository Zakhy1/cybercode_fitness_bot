from django.contrib import admin

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.report import Report
from bot.models.user_state import UserState
from unfold.admin import ModelAdmin


@admin.register(UserState)
class UserStateAdmin(ModelAdmin):
    pass


@admin.register(Cheque)
class ModelNameAdmin(ModelAdmin):
    pass


@admin.register(Contract)
class ContractAdmin(ModelAdmin):
    pass


@admin.register(Circle)
class CircleAdmin(ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    pass
