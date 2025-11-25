import time
from django.utils.deprecation import MiddlewareMixin
from .models import ApiRequestLog, IntegrationApp


class ApiRequestLogMiddleware(MiddlewareMixin):
    """
    Registra requisições da API (rota /api/...), associando à IntegrationApp quando presente.
    """

    def process_request(self, request):
        request._api_start = time.time()

    def process_response(self, request, response):
        path = request.path
        if not path.startswith("/api/"):
            return response

        duration_ms = None
        if hasattr(request, "_api_start"):
            duration_ms = int((time.time() - request._api_start) * 1000)

        app = getattr(request, "auth", None)
        ApiRequestLog.objects.create(
            app=app if isinstance(app, IntegrationApp) else None,
            method=request.method,
            path=path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            remote_ip=self._get_ip(request),
        )
        return response

    def process_exception(self, request, exception):
        path = request.path
        if not path.startswith("/api/"):
            return None
        app = getattr(request, "auth", None)
        duration_ms = None
        if hasattr(request, "_api_start"):
            duration_ms = int((time.time() - request._api_start) * 1000)
        ApiRequestLog.objects.create(
            app=app if isinstance(app, IntegrationApp) else None,
            method=request.method,
            path=path,
            status_code=500,
            duration_ms=duration_ms,
            remote_ip=self._get_ip(request),
            error_message=str(exception)[:500],
        )
        return None

    def _get_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
