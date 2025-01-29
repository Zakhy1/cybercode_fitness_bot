from django.db import models


class UserState(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat ID: {self.chat_id}, State: {self.state}"
