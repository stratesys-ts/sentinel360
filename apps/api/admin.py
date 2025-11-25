from django.contrib import admin
from .models import IntegrationApp
from django.utils.html import format_html


@admin.register(IntegrationApp)
class IntegrationAppAdmin(admin.ModelAdmin):
    change_list_template = "admin/api_dashboard.html"
    list_display = ("name", "is_active", "created_at", "masked_key")
    readonly_fields = ("api_key", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)

    def masked_key(self, obj):
        return f"{obj.api_key[:6]}...{obj.api_key[-4:]}"

    masked_key.short_description = "API Key"

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
