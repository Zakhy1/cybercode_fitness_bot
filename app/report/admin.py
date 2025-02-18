from django.contrib import admin
from django.contrib.admin import ModelAdmin

from report.models.report import Report


@admin.register(Report)
class ReportAdmin(ModelAdmin):
    pass
