from django.db import models


class UserState(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    confirmation_code = models.CharField(max_length=6, null=True, blank=True)
    is_registered = models.BooleanField(default=False)
    has_contract = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    send_reports = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}. сhat ID: {self.chat_id}"

    def get_name(self):
        return self.name
