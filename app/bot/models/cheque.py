from django.db import models


def user_directory_path(instance, filename):
    """Формирует путь для сохранения файлов пользователя"""
    return f"uploads/cheques/user_{instance.user.chat_id}/{filename}"


class Cheque(models.Model):
    user = models.ForeignKey("UserState", on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
