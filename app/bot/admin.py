from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

from bot.models.cheque import Cheque
from bot.models.circle import Circle
from bot.models.contract import Contract
from bot.models.user_state import UserState

from unfold.forms import AdminPasswordChangeForm
from unfold.forms import UserCreationForm
from unfold.forms import UserChangeForm

from unfold.admin import ModelAdmin

admin.site.unregister(User)
admin.site.unregister(Group)




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
    list_display = ['name', 'email', 'state', 'is_registered']
    list_filter = ['is_registered']


@admin.register(Cheque)
class ChequeAdmin(ModelAdmin):
    list_display = ['user', 'uploaded_at']
    list_filter = ['user', 'uploaded_at']


@admin.register(Contract)
class ContractAdmin(ModelAdmin):
    list_display = ['user', 'uploaded_at']
    list_filter = ['user', 'uploaded_at']


@admin.register(Circle)
class CircleAdmin(ModelAdmin):
    list_display = ['user', 'uploaded_at']
    list_filter = ['user', 'uploaded_at']

