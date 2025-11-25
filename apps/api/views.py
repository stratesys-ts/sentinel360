from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_datetime, parse_date
from django.db.models import Q

from apps.projects.models import Project, Issue
from apps.timesheet.models import TimeEntry
from .serializers import ProjectSerializer, IssueSerializer, TimeEntrySerializer
from .models import WebhookSubscription
from .webhooks import dispatch_event
from .authentication import APIKeyAuthentication
from .permissions import HasAPIKey, HasScope


class BaseAPIKeyViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [HasAPIKey]


class ProjectViewSet(BaseAPIKeyViewSet):
    queryset = Project.objects.all().order_by("-created_at")
    serializer_class = ProjectSerializer
    required_scopes = ["projects:read"]
    permission_classes = [HasAPIKey, HasScope]


class IssueViewSet(BaseAPIKeyViewSet):
    queryset = Issue.objects.select_related("project", "assigned_to").order_by("-created_at")
    serializer_class = IssueSerializer
    required_scopes = ["issues:read"]
    permission_classes = [HasAPIKey, HasScope]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")
        project_param = self.request.query_params.get("project")
        updated_after = self.request.query_params.get("updated_after")
        issue_type = self.request.query_params.get("issue_type")

        if status_param:
            qs = qs.filter(status=status_param)
        if project_param:
            qs = qs.filter(project_id=project_param)
        if issue_type:
            qs = qs.filter(issue_type=issue_type)
        if updated_after:
            dt = parse_datetime(updated_after)
            if dt:
                qs = qs.filter(updated_at__gte=dt)
        return qs

    def create(self, request, *args, **kwargs):
        self.required_scopes = ["issues:write"]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        dispatch_event("issue.created", serializer.data, WebhookSubscription.objects.filter(event="issue.created", is_active=True))
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        self.required_scopes = ["issues:write"]
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        dispatch_event("issue.updated", serializer.data, WebhookSubscription.objects.filter(event="issue.updated", is_active=True))
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.required_scopes = ["issues:write"]
        return super().destroy(request, *args, **kwargs)

class TimeEntryViewSet(BaseAPIKeyViewSet,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    queryset = TimeEntry.objects.select_related("project", "task", "timesheet__user").order_by("-date")
    serializer_class = TimeEntrySerializer
    required_scopes = ["timeentries:read"]
    permission_classes = [HasAPIKey, HasScope]

    def get_queryset(self):
        qs = super().get_queryset()
        project_param = self.request.query_params.get("project")
        task_param = self.request.query_params.get("task")
        start_param = self.request.query_params.get("start_date")
        end_param = self.request.query_params.get("end_date")

        if project_param:
            qs = qs.filter(project_id=project_param)
        if task_param:
            qs = qs.filter(task_id=task_param)
        if start_param:
            sd = parse_date(start_param)
            if sd:
                qs = qs.filter(date__gte=sd)
        if end_param:
            ed = parse_date(end_param)
            if ed:
                qs = qs.filter(date__lte=ed)
        return qs

    def create(self, request, *args, **kwargs):
        self.required_scopes = ["timeentries:write"]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        dispatch_event("timeentry.created", serializer.data, WebhookSubscription.objects.filter(event="timeentry.created", is_active=True))
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        self.required_scopes = ["timeentries:write"]
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        dispatch_event("timeentry.updated", serializer.data, WebhookSubscription.objects.filter(event="timeentry.updated", is_active=True))
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        self.required_scopes = ["timeentries:write"]
        return super().destroy(request, *args, **kwargs)


# Public ping endpoint (sem API Key) para health-check
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})
