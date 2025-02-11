from django.db import models


class UserState(models.Model):
    chat_id = models.BigIntegerField(unique=True, verbose_name="ID чата")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="ФИО")
    state = models.CharField(max_length=255, null=True, blank=True, verbose_name="Состояние")
    email = models.EmailField(null=True, blank=True, verbose_name="Адрес электронной почты")
    confirmation_code = models.CharField(max_length=6, null=True, blank=True, verbose_name="Код подтверждения")
    is_registered = models.BooleanField(default=False, verbose_name="Зарегистрирован")
    has_contract = models.BooleanField(default=False, verbose_name="Договор загружен")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    send_reports = models.BooleanField(default=False, verbose_name="Отправлять отчеты")
    banned = models.BooleanField(default=False, verbose_name="Заблокирован")

    def __str__(self):
        return f"{self.name}. сhat ID: {self.chat_id}"

    def get_name(self):
        return self.name

    class Meta:
        verbose_name = "Состояние пользователя"
        verbose_name_plural = "Состояния пользователей"
