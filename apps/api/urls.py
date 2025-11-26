from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import ProjectViewSet, IssueViewSet, TimeEntryViewSet, HealthView

router = DefaultRouter()
router.register(r"v1/projects", ProjectViewSet, basename="api-projects")
router.register(r"v1/issues", IssueViewSet, basename="api-issues")
router.register(r"v1/time-entries", TimeEntryViewSet, basename="api-time-entries")

schema_view = get_schema_view(
    openapi.Info(
        title="Sentinel 360 API",
        default_version="v1",
        description="API pública do Sentinel 360 para integrações (projects, issues, time entries).",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="api-health"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),
    path("", include(router.urls)),
]
