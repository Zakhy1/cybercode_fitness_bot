from django.db import models


class UserState(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    confirmation_code = models.CharField(max_length=6, null=True, blank=True)
    is_registered = models.BooleanField(default=False)
    has_contract = models.BooleanField(default=False)  # Флаг наличия договора
    receive_notifications = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat ID: {self.chat_id}, Registered: {self.is_registered}, Has contract: {self.has_contract}"
