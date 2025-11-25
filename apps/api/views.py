from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.projects.models import Project, Task
from apps.timesheet.models import TimeEntry
from .serializers import ProjectSerializer, TaskSerializer, TimeEntrySerializer
from .authentication import APIKeyAuthentication
from .permissions import HasAPIKey


class BaseAPIKeyViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [HasAPIKey]


class ProjectViewSet(BaseAPIKeyViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    serializer_class = ProjectSerializer


class TaskViewSet(BaseAPIKeyViewSet):
    queryset = Task.objects.select_related("project", "assigned_to").order_by("-created_at")
    serializer_class = TaskSerializer


class TimeEntryViewSet(BaseAPIKeyViewSet):
    queryset = TimeEntry.objects.select_related("project", "task", "timesheet__user").order_by("-date")
    serializer_class = TimeEntrySerializer


# Public ping endpoint (sem API Key) para health-check
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})
