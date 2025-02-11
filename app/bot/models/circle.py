from django.db import models


def user_directory_path(instance, filename):
    """Формирует путь для сохранения файлов пользователя"""
    return f"uploads/contracts/user_{instance.user.chat_id}/{filename}"


class Circle(models.Model):
    user = models.ForeignKey("UserState", on_delete=models.CASCADE, verbose_name="Пользователь")
    file = models.FileField(upload_to=user_directory_path, verbose_name="Видео")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружен")

    def __str__(self):
        return f"Кружок от {self.user.get_name()} {self.uploaded_at}"

    class Meta:
        verbose_name = "Кружок"
        verbose_name_plural = "Кружки"