from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.report import Report
from bot.models.user_state import UserState
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

admin.site.unregister(User)
admin.site.unregister(Group)
# @admin.register(ModelName)
# class ModelNameAdmin(admin.ModelAdmin):
#     list_display = ['']
#     list_filter = ['']
#     fields = ['']
#     inlines = []
#     raw_id_fields = ['']
#     readonly_fields = ['']
#     search_fields = ['']
#     ordering = ['']
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(UserState)
class UserStateAdmin(ModelAdmin):
    pass


@admin.register(Cheque)
class ModelChequeAdmin(ModelAdmin):
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
