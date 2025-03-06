from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError


class ReportForm(forms.Form):
    date_start = forms.DateField(
        widget=forms.TextInput(
            attrs={'class': 'form-control date-picker'}), label="Дата начала периода"
    )
    date_end = forms.DateField(
        widget=forms.TextInput(
            attrs={'class': 'form-control date-picker'}), label="Дата конца периода"
    )

    def clean(self):
        cleaned_data = super().clean()

        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if not date_start or not date_end:
            raise ValidationError("Оба поля даты должны быть заполнены")

        if date_end < date_start:
            raise ValidationError("Дата конца раньше даты начала")

        return cleaned_data
