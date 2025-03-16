import datetime

from django.views.generic import ListView

from bot.models.circle import Circle


class CircleHistoryView(ListView):
    template_name = "report/circle_history.html"
    model = Circle  # Указываем модель

    def get_queryset(self):
        date_start = self.request.GET.get("date_start")
        date_end = self.request.GET.get("date_end")
        user_id = self.kwargs.get('pk')

        # Исправленное условие
        if not date_start or not date_end or not user_id:
            return []

        try:
            start_date = datetime.datetime.strptime(date_start, "%d.%m.%Y")
            end_date = datetime.datetime.strptime(date_end, "%d.%m.%Y")
        except ValueError:
            return []

        circles_by_range = Circle.objects.filter(
            user_id=user_id,
            uploaded_at__gte=start_date,
            uploaded_at__lte=end_date
        )

        # Отладочный вывод
        return circles_by_range
