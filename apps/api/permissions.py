from rest_framework.permissions import BasePermission


class HasAPIKey(BasePermission):
    """
    Permite acesso apenas se a autenticação via API Key ocorreu.
    """

    def has_permission(self, request, view):
        return bool(getattr(request, "auth", None))


class HasScope(BasePermission):
    """
    Verifica se a IntegrationApp possui o escopo exigido pela view.
    """

    def has_permission(self, request, view):
        app = getattr(request, "auth", None)
        required = getattr(view, "required_scopes", [])
        if not required:
            return True
        scopes = set(getattr(app, "scopes", []) or [])
        return any(scope in scopes for scope in required)
