import secrets
from django.db import models
from django.utils import timezone


class IntegrationApp(models.Model):
    """Cliente externo autorizado a usar a API via API Key."""

    name = models.CharField(max_length=150, unique=True)
    api_key = models.CharField(max_length=64, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    scopes = models.JSONField(default=list, blank=True, help_text="Lista de escopos permitidos (ex.: projects:read, issues:write)")
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


class WebhookSubscription(models.Model):
    """Inscrição de webhook para eventos de integração."""
    EVENT_CHOICES = [
        ("issue.created", "issue.created"),
        ("issue.updated", "issue.updated"),
        ("timeentry.created", "timeentry.created"),
        ("timeentry.updated", "timeentry.updated"),
    ]
    app = models.ForeignKey(IntegrationApp, on_delete=models.CASCADE, related_name="webhooks")
    target_url = models.URLField()
    event = models.CharField(max_length=50, choices=EVENT_CHOICES)
    secret = models.CharField(max_length=64, blank=True, help_text="Assinatura HMAC opcional")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = secrets.token_hex(16)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event} -> {self.target_url}"


class ApiRequestLog(models.Model):
    """Auditoria de requisições da API."""
    app = models.ForeignKey(IntegrationApp, null=True, blank=True, on_delete=models.SET_NULL, related_name="logs")
    method = models.CharField(max_length=8)
    path = models.CharField(max_length=255)
    status_code = models.PositiveIntegerField()
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    remote_ip = models.GenericIPAddressField(null=True, blank=True)
    error_message = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Log de requisição"
        verbose_name_plural = "Logs de requisição"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.method} {self.path} [{self.status_code}]"


class WebhookDeliveryLog(models.Model):
    """Log de entregas de webhooks por inscrição."""
    subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE, related_name="deliveries")
    event = models.CharField(max_length=50)
    target_url = models.URLField()
    status_code = models.PositiveIntegerField(null=True, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.CharField(max_length=500, blank=True)
    response_body = models.TextField(blank=True)
    attempt = models.PositiveIntegerField(default=1)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        verbose_name = "Entrega de Webhook"
        verbose_name_plural = "Entregas de Webhook"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event} -> {self.target_url} (tentativa {self.attempt})"
