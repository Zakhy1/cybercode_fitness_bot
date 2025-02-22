from django import forms


class ReportForm(forms.Form):
    date_start = forms.DateField(
        widget=forms.TextInput(
            attrs={'class': 'form-control date-picker'}), label="Период:"
    )
    date_end = forms.DateField(
        widget=forms.TextInput(
            attrs={'class': 'form-control date-picker'}), label=""
    )

    # def is_valid(self):
    #     return super().is_valid()
