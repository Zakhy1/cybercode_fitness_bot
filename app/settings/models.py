from django.db import models


class Settings(models.Model):
    name = models.CharField(max_length=255, verbose_name="наименование")
    prefix = models.CharField(max_length=100, verbose_name="префикс", default="general")
    value = models.CharField(max_length=255, verbose_name="значение", default="")

    def get_setting(self, name) -> str | None:
        try:
            value = self.objects.filter(name=name).first().value
            return value
        except AttributeError:
            return None

    def set_setting(self, name, value) -> None:
        setting = self.objects.get_or_create(name=name)
        setting[0].value = value
        setting[0].save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "настройка"
        verbose_name_plural = "настройки"
