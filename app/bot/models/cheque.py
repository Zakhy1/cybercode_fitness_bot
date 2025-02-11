from django.db import models


def user_directory_path(instance, filename):
    """Формирует путь для сохранения файлов пользователя"""
    return f"uploads/cheques/user_{instance.user.chat_id}/{filename}"


class Cheque(models.Model):
    user = models.ForeignKey("UserState", on_delete=models.CASCADE, verbose_name="Пользователь")
    file = models.FileField(upload_to=user_directory_path, verbose_name="Файл договора")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружен")

    class Meta:
        verbose_name = "Чек"
        verbose_name_plural = "Чеки"

    def __str__(self):
        return f"Чек {self.user.get_name()} от {self.uploaded_at}"