import secrets
from django.db import models
from django.utils import timezone


class IntegrationApp(models.Model):
    """Cliente externo autorizado a usar a API via API Key."""

    name = models.CharField(max_length=150, unique=True)
    api_key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Aplicação de Integração"
        verbose_name_plural = "Aplicações de Integração"

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
