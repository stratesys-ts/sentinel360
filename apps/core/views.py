from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from apps.helpdesk.models import Ticket
from django.db.models import Q

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_client():
            return reverse_lazy('core:portal_dashboard')
        return reverse_lazy('core:dashboard')

    def form_valid(self, form):
        user = form.get_user()
        # Prevent clients from logging in via the main login page (login.html)
        if self.template_name == 'login.html' and user.is_client():
            form.add_error(None, "Acesso não permitido")
            return self.form_invalid(form)
        return super().form_valid(form)

def portal_login(request):
    return CustomLoginView.as_view(template_name='login_portal.html')(request)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_client():
            return redirect('core:portal_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Import models inside method to avoid circular imports if any
        from apps.projects.models import Project, Task
        from apps.timesheet.models import TimeEntry
        from django.utils import timezone
        from django.db.models import Sum, Q
        
        user = self.request.user

        # Tickets: apenas os relacionados ao usuário (criador ou responsável)
        context['open_tickets_count'] = Ticket.objects.filter(
            status='OPEN'
        ).filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).distinct().count()
        
        # Horas no mês: apenas do usuário logado
        now = timezone.now()
        entries = TimeEntry.objects.filter(
            date__year=now.year,
            date__month=now.month,
            timesheet__user=user
        )
        total_hours = entries.aggregate(total=Sum('hours'))['total'] or 0
        context['total_hours_month'] = f"{int(total_hours)}h"
        
        # Projetos: apenas os visíveis ao usuário
        if user.is_superuser or user.has_perm('projects.view_project') or user.has_perm('projects.change_project'):
            projects_qs = Project.objects.all()
        elif user.is_client():
            projects_qs = Project.objects.filter(
                external_access=True
            ).filter(Q(client=user) | Q(team=user))
        else:
            projects_qs = Project.objects.filter(
                Q(team=user) | Q(project_manager=user) | Q(project_owner=user)
            )
        context['active_projects_count'] = projects_qs.filter(status=Project.Status.IN_PROGRESS).distinct().count()
        
        # Tasks assigned to the current user (any status)
        context['my_tasks_count'] = Task.objects.filter(assigned_to=user).count()
        
        return context


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    template_name = 'search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        user = self.request.user

        from apps.projects.models import Project, Task
        from apps.timesheet.models import Timesheet

        results = {
            'tickets': [],
            'projects': [],
            'tasks': [],
            'timesheets': [],
        }

        if query:
            # Tickets: apenas se o usuário tem perm e é criador/atribuído
            if user.has_perm('helpdesk.view_ticket'):
                ticket_filter = Q(title__icontains=query) | Q(description__icontains=query)
                # Busca por ID (#123 ou 123) incluindo public_id
                num = query.lstrip('#')
                if num.isdigit():
                    ticket_filter |= Q(id=int(num)) | Q(public_id=int(num))
                tickets_qs = Ticket.objects.filter(ticket_filter).filter(
                    Q(created_by=user) | Q(assigned_to=user)
                ).distinct()[:10]
                results['tickets'] = tickets_qs

            # Projetos
            if user.has_perm('projects.view_project'):
                results['projects'] = Project.objects.filter(
                    Q(name__icontains=query) | Q(description__icontains=query)
                ).distinct()[:10]

            # Tarefas: limitadas às atribuídas se não for staff
            if user.has_perm('projects.view_task'):
                task_filter = Q(title__icontains=query) | Q(description__icontains=query)
                num = query.lstrip('#')
                if num.isdigit():
                    task_filter |= Q(id=int(num)) | Q(public_id=int(num))
                if not user.is_staff:
                    task_filter &= Q(assigned_to=user)
                results['tasks'] = Task.objects.filter(task_filter).distinct()[:10]

            # Timesheets: próprias; se staff, todas
            if user.has_perm('timesheet.view_timesheet'):
                ts_filter = Q(user=user) if not user.is_staff else Q()
                results['timesheets'] = Timesheet.objects.filter(
                    ts_filter & (
                        Q(user__username__icontains=query) |
                        Q(status__icontains=query)
                    )
                ).select_related('user').distinct()[:10]

        context['query'] = query
        context['results'] = results
        return context


class FAQView(LoginRequiredMixin, TemplateView):
    template_name = 'faq.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user
        return context

@login_required
def portal_dashboard(request):
    if not request.user.is_client():
        return redirect('core:dashboard')
    
    tickets = []
    stats = {
        'open': 0,
        'in_progress': 0,
        'closed': 0
    }

    if request.user.client_project:
        tickets = Ticket.objects.filter(project=request.user.client_project).order_by('-created_at')
        
        stats['open'] = tickets.filter(status='OPEN').count()
        stats['in_progress'] = tickets.filter(status='IN_PROGRESS').count()
        stats['closed'] = tickets.filter(status__in=['RESOLVED', 'CLOSED']).count()
    
    context = {
        'tickets': tickets[:5], # Show only recent 5
        'stats': stats
    }
    
    return render(request, 'portal/dashboard.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    next_page = request.GET.get('next', 'core:login')
    logout(request)
    return redirect(next_page)

from django.views.generic import ListView, CreateView
from django.contrib.auth import get_user_model
from .forms import ExternalUserForm, InternalUserForm

User = get_user_model()

class StaffOnlyMixin(UserPassesTestMixin):
    """Restrict access to internal staff (manager/admin/superuser)."""

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role in [User.Role.ADMIN, User.Role.MANAGER]

    def handle_no_permission(self):
        return redirect('core:dashboard')


class InternalUserListView(LoginRequiredMixin, StaffOnlyMixin, ListView):
    model = User
    template_name = 'core/user_list_internal.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.exclude(role=User.Role.CLIENT)

class InternalUserCreateView(LoginRequiredMixin, StaffOnlyMixin, CreateView):
    model = User
    form_class = InternalUserForm
    template_name = 'core/user_form_internal.html'
    success_url = reverse_lazy('core:internal_user_list')

    def form_valid(self, form):
        return super().form_valid(form)

class ExternalUserListView(LoginRequiredMixin, StaffOnlyMixin, ListView):
    model = User
    template_name = 'core/user_list_external.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(role=User.Role.CLIENT)

class ExternalUserCreateView(LoginRequiredMixin, StaffOnlyMixin, CreateView):
    model = User
    form_class = ExternalUserForm
    template_name = 'core/user_form_external.html'
    success_url = reverse_lazy('core:external_user_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Here you might want to send an email with the generated password
        # For now, we'll just pass it to the template via session or messages if needed
        # But since we redirect, maybe we show it in a success message?
        # For simplicity in this step, we'll just let it redirect. 
        # The user._generated_password contains the password.
        return response
