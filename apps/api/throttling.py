from rest_framework.throttling import SimpleRateThrottle


class APIKeyRateThrottle(SimpleRateThrottle):
    """
    Limita requisições por API Key (fallback por IP se não houver auth).
    """
    scope = "api"

    def get_cache_key(self, request, view):
        ident = None
        if getattr(request, "auth", None):
            ident = getattr(request.auth, "api_key", None)
        if not ident:
            ident = self.get_ident(request)
        return self.cache_key % {"scope": self.scope, "ident": ident}
