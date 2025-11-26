from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from apps.projects.models import Issue
from .forms import TicketForm

class HelpdeskAccessMixin(PermissionRequiredMixin):
    permission_required = 'core.access_helpdesk'
    raise_exception = True


class TicketListView(LoginRequiredMixin, HelpdeskAccessMixin, ListView):
    model = Issue
    template_name = 'helpdesk/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 10

    def get_queryset(self):
        queryset = Issue.objects.filter(issue_type=Issue.IssueType.HELP_DESK)
        user = self.request.user

        if user.is_client():
            queryset = queryset.filter(created_by=user)
        elif user.is_collaborator():
            queryset = queryset.filter(Q(created_by=user) | Q(assigned_to=user))
        return queryset.order_by('-created_at')


class TicketCreateView(LoginRequiredMixin, HelpdeskAccessMixin, CreateView):
    model = Issue
    form_class = TicketForm
    template_name = 'helpdesk/ticket_form.html'
    success_url = reverse_lazy('helpdesk:ticket_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.issue_type = Issue.IssueType.HELP_DESK
        return super().form_valid(form)


class TicketDetailView(LoginRequiredMixin, HelpdeskAccessMixin, DetailView):
    model = Issue
    template_name = 'helpdesk/ticket_detail.html'
    context_object_name = 'ticket'

    def get_queryset(self):
        base_qs = Issue.objects.filter(issue_type=Issue.IssueType.HELP_DESK)
        user = self.request.user
        if user.is_client():
            return base_qs.filter(created_by=user)
        if user.is_collaborator():
            return base_qs.filter(Q(created_by=user) | Q(assigned_to=user))
        return base_qs


class TicketUpdateView(LoginRequiredMixin, HelpdeskAccessMixin, UpdateView):
    model = Issue
    form_class = TicketForm
    template_name = 'helpdesk/ticket_form.html'
    success_url = reverse_lazy('helpdesk:ticket_list')

    def get_queryset(self):
        qs = Issue.objects.filter(issue_type=Issue.IssueType.HELP_DESK)
        user = self.request.user
        if user.is_superuser or user.is_staff or user.is_manager():
            return qs
        return qs.filter(created_by=user)

    def form_valid(self, form):
        form.instance.issue_type = Issue.IssueType.HELP_DESK
        return super().form_valid(form)
