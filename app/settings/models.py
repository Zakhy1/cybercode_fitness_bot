from django.db import models


class Settings(models.Model):
    name = models.CharField(max_length=255, verbose_name="наименование")
    prefix = models.CharField(max_length=100, verbose_name="префикс",
                              default="general", null=True, blank=True)
    value = models.CharField(max_length=255, verbose_name="значение",
                             default="", null=True, blank=True)

    @classmethod
    def get_setting(cls, name: str, default: str = "") -> str | None:
        try:
            value = cls.objects.filter(name=name).first().value
            return value
        except AttributeError:
            cls.objects.create(name=name, value=default)
            return default

    @classmethod
    def set_setting(cls, name, value) -> None:
        setting = cls.objects.get_or_create(name=name)
        setting[0].value = value
        setting[0].save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "настройка"
        verbose_name_plural = "настройки"
