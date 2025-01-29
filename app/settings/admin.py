from .models import Settings
from django.contrib import admin


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
    list_editable = ("value",)
