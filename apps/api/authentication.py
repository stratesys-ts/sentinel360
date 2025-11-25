from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import IntegrationApp


class APIKeyAuthentication(BaseAuthentication):
    """
    Autenticação por API Key via header X-API-Key.
    """
    keyword = "X-API-Key"

    def authenticate(self, request):
        api_key = request.headers.get(self.keyword) or request.META.get(f"HTTP_{self.keyword.replace('-', '_')}")
        if not api_key:
            return None

        try:
            app = IntegrationApp.objects.get(api_key=api_key, is_active=True)
        except IntegrationApp.DoesNotExist:
            raise exceptions.AuthenticationFailed("API Key inválida ou inativa.")

        # Usuário anônimo representando a app; permissões adicionais podem ser aplicadas depois
        return (None, app)
