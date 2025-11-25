from django.contrib import admin
from .models import IntegrationApp, WebhookSubscription, ApiRequestLog, WebhookDeliveryLog
from django.utils.html import format_html


@admin.register(IntegrationApp)
class IntegrationAppAdmin(admin.ModelAdmin):
    change_list_template = "admin/api_dashboard.html"
    list_display = ("name", "is_active", "created_at", "masked_key", "scopes_list")
    readonly_fields = ("api_key", "created_at")
    search_fields = ("name", "api_key")
    list_filter = ("is_active",)
    filter_horizontal = ()

    def masked_key(self, obj):
        return f"{obj.api_key[:6]}...{obj.api_key[-4:]}"

    masked_key.short_description = "API Key"

    def scopes_list(self, obj):
        return ", ".join(obj.scopes or [])
    scopes_list.short_description = "Escopos"

    def changelist_view(self, request, extra_context=None):
        # Usa o dashboard personalizado como lista
        context = extra_context or {}
        base_url = request.build_absolute_uri("/api/").rstrip("/") + "/"
        context.update(
            {
                "title": "API & Integrações",
                "base_url": base_url,
                "docs_url": request.build_absolute_uri("/api/docs/"),
                "health_url": request.build_absolute_uri("/api/health/"),
                "integrations": [
                    {
                        "name": "Power BI",
                        "desc": "Dashboards e datasets via API ou arquivos CSV/Excel gerados.",
                        "cta": "Ver documentação",
                        "url": "https://learn.microsoft.com/power-bi/connect-data/service-connect-data",
                    },
                    {
                        "name": "Power Automate",
                        "desc": "Automatize fluxos chamando endpoints REST autenticados.",
                        "cta": "Ver documentação",
                        "url": "https://learn.microsoft.com/power-automate/",
                    },
                    {
                        "name": "Jira",
                        "desc": "Sincronize issues/tarefas e status entre Jira e o ERP.",
                        "cta": "Ver documentação",
                        "url": "https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/",
                    },
                    {
                        "name": "ServiceNow",
                        "desc": "Integre incidentes e mudanças com a central de serviços.",
                        "cta": "Ver documentação",
                        "url": "https://developer.servicenow.com/",
                    },
                ],
                "guide_url": "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Introduction",
                "endpoints": [
                    {"method": "GET", "path": "v1/projects/", "desc": "Lista projetos."},
                    {"method": "GET", "path": "v1/tasks/", "desc": "Lista tarefas com projeto e responsável."},
                    {"method": "GET", "path": "v1/time-entries/", "desc": "Lista lançamentos de horas (timesheets)."},
                    {"method": "GET", "path": "health/", "desc": "Ping de saúde (sem auth)."},
                    {"method": "GET", "path": "docs/", "desc": "Swagger UI da API."},
                ],
                "auth_header": "X-API-Key",
            }
        )
        return super().changelist_view(request, extra_context=context)


@admin.register(WebhookSubscription)
class WebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("event", "target_url", "app", "is_active", "created_at")
    list_filter = ("event", "is_active")
    search_fields = ("target_url", "app__name")
    autocomplete_fields = ("app",)


@admin.register(ApiRequestLog)
class ApiRequestLogAdmin(admin.ModelAdmin):
    list_display = ("method_badge", "path", "status_badge", "app", "duration_ms", "created_at")
    list_filter = ("method", "status_code", "app")
    search_fields = ("path", "app__name", "remote_ip", "error_message")
    readonly_fields = ("app", "method", "path", "status_code", "duration_ms", "remote_ip", "error_message", "created_at")
    ordering = ("-created_at",)
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Método")
    def method_badge(self, obj):
        color = {
            "GET": "#0ea5e9",
            "POST": "#22c55e",
            "PUT": "#f59e0b",
            "PATCH": "#f59e0b",
            "DELETE": "#ef4444",
        }.get(obj.method, "#6b7280")
        return format_html('<span class="badge-log" style="background:{};">{}</span>', color, obj.method)

    @admin.display(description="Status")
    def status_badge(self, obj):
        color = "#22c55e" if 200 <= obj.status_code < 300 else "#f97316" if obj.status_code and obj.status_code < 500 else "#ef4444"
        return format_html('<span class="badge-log" style="background:{};">{}</span>', color, obj.status_code)


@admin.register(WebhookDeliveryLog)
class WebhookDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("event", "target_url", "status_badge", "success_icon", "attempt", "subscription", "created_at")
    list_filter = ("event", "success", "status_code")
    search_fields = ("target_url", "subscription__app__name", "error_message")
    readonly_fields = ("subscription", "event", "target_url", "status_code", "success", "error_message", "response_body", "attempt", "duration_ms", "created_at")
    ordering = ("-created_at",)
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Status")
    def status_badge(self, obj):
        color = "#22c55e" if obj.success else "#ef4444"
        code = obj.status_code or "-"
        return format_html('<span class="badge-log" style="background:{};">{}</span>', color, code)

    @admin.display(description="OK?")
    def success_icon(self, obj):
        return format_html('<span style="color:{};">{}</span>', "#16a34a" if obj.success else "#ef4444", "●")
