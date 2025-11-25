
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q, Sum
from decimal import Decimal
from .models import Project, Task
from .forms import ProjectForm, TaskForm
from apps.timesheet.models import TimeEntry


class ProjectAccessMixin:
    """Centralize project visibility rules."""
    def get_project_queryset(self):
        qs = Project.objects.all()
        user = self.request.user

        if user.is_superuser or user.has_perm('projects.view_project') or user.has_perm('projects.change_project'):
            return qs

        if getattr(user, 'role', None) == user.Role.CLIENT:
            return qs.filter(
                external_access=True
            ).filter(
                Q(client=user) | Q(team=user)
            )

        return qs.filter(
            Q(team=user) |
            Q(project_manager=user) |
            Q(project_owner=user)
        )


class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, ProjectAccessMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')
    permission_required = 'projects.change_project'
    raise_exception = True

    def get_queryset(self):
        return self.get_project_queryset()

class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, ProjectAccessMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:project_list')
    permission_required = 'projects.delete_project'
    raise_exception = True

    def get_queryset(self):
        return self.get_project_queryset()

class ProjectListView(LoginRequiredMixin, ProjectAccessMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        from django.db.models import Sum
        
        qs = self.get_project_queryset()
        return qs.annotate(
            total_hours=Sum('time_entries__hours')
        ).order_by('-created_at')

class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:project_list')
    permission_required = 'projects.add_project'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if getattr(user, 'role', None) == user.Role.CLIENT:
            return redirect('core:portal_dashboard')
        return super().dispatch(request, *args, **kwargs)

class ProjectDetailView(LoginRequiredMixin, ProjectAccessMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'

    def get_queryset(self):
        return self.get_project_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
        context['task_form'] = TaskForm()
        context['active_tab'] = 'geral'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = self.object
            task.save()
            return redirect('projects:project_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(task_form=form))

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['status']
    template_name = 'projects/task_update_status.html' # Not used directly, usually via AJAX or simple redirect

    def get_queryset(self):
        qs = super().get_queryset().select_related('project')
        user = self.request.user
        if user.is_superuser or user.has_perm('projects.change_project'):
            return qs
        if getattr(user, 'role', None) == user.Role.CLIENT:
            return qs.filter(
                project__external_access=True
            ).filter(
                Q(project__client=user) | Q(project__team=user)
            )
        return qs.filter(
            Q(project__team=user) |
            Q(project__project_manager=user) |
            Q(project__project_owner=user)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        new_status = request.POST.get('status')
        if new_status in dict(Task.Status.choices):
            self.object.status = new_status
            self.object.save()
        return redirect('projects:project_detail', pk=self.object.project.pk)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'projects/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        qs = super().get_queryset().select_related('project', 'assigned_to')
        user = self.request.user
        if user.is_superuser or user.has_perm('projects.view_project'):
            return qs
        if getattr(user, 'role', None) == user.Role.CLIENT:
            return qs.filter(
                project__external_access=True
            ).filter(
                Q(project__client=user) | Q(project__team=user)
            )
        return qs.filter(
            Q(project__team=user) |
            Q(project__project_manager=user) |
            Q(project__project_owner=user) |
            Q(assigned_to=user)
        )


class ProjectTasksView(LoginRequiredMixin, ProjectAccessMixin, TemplateView):
    template_name = 'projects/project_tasks.html'

    def get_project(self):
        return get_object_or_404(self.get_project_queryset(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context['project'] = project
        context['tasks'] = project.tasks.all().select_related('assigned_to')
        context['active_tab'] = 'tarefas'
        return context


class ProjectKanbanView(LoginRequiredMixin, ProjectAccessMixin, TemplateView):
    template_name = 'projects/project_kanban.html'

    def get_project(self):
        return get_object_or_404(self.get_project_queryset(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context['project'] = project
        context['todo_tasks'] = project.tasks.filter(status=Task.Status.TODO)
        context['doing_tasks'] = project.tasks.filter(status=Task.Status.DOING)
        context['done_tasks'] = project.tasks.filter(status=Task.Status.DONE)
        context['active_tab'] = 'kanban'
        return context


class ProjectRisksView(LoginRequiredMixin, ProjectAccessMixin, TemplateView):
    template_name = 'projects/project_risks.html'

    def get_project(self):
        return get_object_or_404(self.get_project_queryset(), pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_project()
        context['active_tab'] = 'riscos'
        return context


class QuickTaskCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/task_quick_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()

        project_id = self.request.GET.get('project')
        selected_project = None
        if project_id:
            selected_project = Project.objects.filter(pk=project_id).first()

        context['projects'] = Project.objects.all().order_by('name')
        context['internal_users'] = User.objects.filter(is_active=True).exclude(role=User.Role.CLIENT).order_by('username')
        context['selected_project'] = selected_project
        # Define para onde o botão Cancelar deve voltar. Prioriza a tela anterior, senão cai no projeto ou dashboard.
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            cancel_url = referer
        elif selected_project:
            cancel_url = reverse('projects:project_tasks', kwargs={'pk': selected_project.pk})
        else:
            cancel_url = reverse('core:dashboard')
        context['cancel_url'] = cancel_url
        return context

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        project_id = request.POST.get('project')
        assigned_id = request.POST.get('assigned_to') or None
        due_date_raw = request.POST.get('due_date')
        start_date_raw = request.POST.get('start_date')

        errors = []
        project = None

        if not title:
            errors.append('Título')

        if not project_id:
            errors.append('Projeto')
        else:
            project = Project.objects.filter(pk=project_id).first()
            if not project:
                errors.append('Projeto inválido')

        start_date = None
        due_date = None
        if start_date_raw:
            try:
                start_date = datetime.fromisoformat(start_date_raw).date()
            except ValueError:
                errors.append('Data Início inválida')
        if due_date_raw:
            try:
                due_date = datetime.fromisoformat(due_date_raw).date()
            except ValueError:
                errors.append('Data Fim inválida')

        if errors:
            messages.error(request, 'Preencha corretamente: ' + ', '.join(errors))
            return self.get(request, *args, **kwargs)

        task = Task.objects.create(
            project=project,
            title=title,
            description=description,
            start_date=start_date,
            due_date=due_date,
        )

        if assigned_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            assigned = User.objects.filter(pk=assigned_id).first()
            if assigned:
                task.assigned_to = assigned
                task.save(update_fields=['assigned_to'])

        messages.success(request, 'Tarefa criada com sucesso.')
        return redirect('projects:project_tasks', pk=project.pk)


class TaskAssignedListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'projects/task_assigned_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user).order_by('-due_date', 'title')


class ProjectHoursView(LoginRequiredMixin, ProjectAccessMixin, ListView):
    model = TimeEntry
    template_name = 'projects/project_hours.html'
    context_object_name = 'time_entries'
    paginate_by = 50

    def get_project(self):
        return get_object_or_404(self.get_project_queryset(), pk=self.kwargs['pk'])

    def get_queryset(self):
        project = self.get_project()
        qs = TimeEntry.objects.filter(project=project).select_related(
            'project', 'task', 'activity', 'timesheet__user'
        ).order_by('-date')

        user = self.request.user
        # Full access if global view/change permission or superuser
        if user.is_superuser or user.has_perm('timesheet.view_timeentry') or user.has_perm('timesheet.change_timeentry'):
            return qs

        # Otherwise only if user can access the project (ProjectAccessMixin)
        allowed_project = self.get_project_queryset().filter(pk=project.pk)
        if allowed_project.exists():
            return qs

        return TimeEntry.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        entries = context['time_entries']
        total_hours = entries.aggregate(total=Sum('hours'))['total'] or 0
        per_user_total = entries.values('timesheet__user__username').annotate(total=Sum('hours'))

        # Group entries by month
        month_groups = []
        grouped = {}
        for entry in entries:
            key = entry.date.strftime('%Y-%m')
            if key not in grouped:
                grouped[key] = {
                    'label': entry.date.strftime('%b/%Y'),
                    'entries': [],
                }
            grouped[key]['entries'].append(entry)

        # Aggregate hours per user inside each month group
        for key, data in grouped.items():
            per_user = {}
            for e in data['entries']:
                username = e.timesheet.user.username if e.timesheet and e.timesheet.user else '-'
                per_user[username] = per_user.get(username, Decimal('0')) + (e.hours or Decimal('0'))
            data['per_user'] = [{'user': u, 'hours': h} for u, h in per_user.items()]
            data['total'] = sum(per_user.values()) if per_user else Decimal('0')
            # Order users by hours desc then name
            data['per_user'].sort(key=lambda x: (-x['hours'], x['user']))
            month_groups.append((key, data))

        # Sort months desc
        month_groups.sort(key=lambda x: x[0], reverse=True)

        context.update({
            'project': project,
            'total_hours': total_hours,
            'hours_per_user': per_user_total,
            'month_groups': month_groups,
        })
        return context
