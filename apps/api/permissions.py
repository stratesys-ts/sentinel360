from rest_framework.permissions import BasePermission


class HasAPIKey(BasePermission):
    """
    Permite acesso apenas se a autenticação via API Key ocorreu.
    """

    def has_permission(self, request, view):
        return bool(getattr(request, "auth", None))
