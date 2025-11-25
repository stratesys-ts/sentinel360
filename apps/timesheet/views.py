from collections import defaultdict
import calendar
from datetime import timedelta, datetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import IntegrityError, models
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
import json
import csv
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from django.views import View, generic
try:
    import openpyxl
except ImportError:
    openpyxl = None
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    letter = None
    canvas = None
from .models import TimeEntry, Timesheet, Activity
from apps.projects.models import Project, Task
from .forms import ActivityForm, TimeEntryForm, TimesheetForm

class TimesheetListView(LoginRequiredMixin, ListView):
    model = Timesheet
    template_name = 'timesheet/timesheet_list.html'
    context_object_name = 'timesheets'
    paginate_by = 20

    def get_queryset(self):
        return Timesheet.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timesheets = self.get_queryset()

        grouped = defaultdict(list)
        for ts in timesheets:
            key = ts.start_date.strftime('%Y-%m')
            grouped[key].append(ts)

        grouped_ordered = []
        for key in sorted(grouped.keys(), reverse=True):
            year, month = key.split('-')
            month_name = calendar.month_name[int(month)]
            # Mapeia para pt-BR
            month_pt = {
                'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
                'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
                'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
                'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
            }.get(month_name, month_name)
            grouped_ordered.append({
                'month_year': f'{month_pt} {year}',
                'timesheets': grouped[key]
            })

        context['grouped_timesheets'] = grouped_ordered
        return context

class TimesheetApprovalListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Timesheet
    template_name = 'timesheet/timesheet_approval_list.html'
    context_object_name = 'timesheets'
    paginate_by = 20
    permission_required = 'core.access_approvals'
    raise_exception = True

    def has_permission(self):
        user = self.request.user
        # Gestores podem aprovar mesmo sem permissão explícita no grupo
        if getattr(user, 'role', None) == getattr(user, 'Role', None).MANAGER:
            return True
        return super().has_permission()

    def get_queryset(self):
        user = self.request.user
        if not (getattr(user, 'role', None) == getattr(user, 'Role', None).MANAGER or user.has_perm('timesheet.change_timesheet') or user.is_superuser):
            return Timesheet.objects.none()

        qs = Timesheet.objects.filter(
            Q(status=Timesheet.Status.SUBMITTED) | Q(status=Timesheet.Status.PARTIALLY_APPROVED)
        ).filter(
            entries__project__project_manager=user
        ).exclude(
            partial_approvers=user
        ).distinct().order_by('-start_date')

        if user.has_perm('timesheet.change_timesheet') or user.is_superuser:
            return qs

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TimesheetCreateView(LoginRequiredMixin, CreateView):
    model = Timesheet
    form_class = TimesheetForm
    # fields = ['start_date']
    success_url = reverse_lazy('timesheet:timesheet_list')

    def form_valid(self, form):
        timesheet = form.save(commit=False)
        timesheet.user = self.request.user
        # Calculate end_date (start_date + 6 days)
        timesheet.end_date = timesheet.start_date + timedelta(days=6)
        try:
            timesheet.save()
        except IntegrityError:
            form.add_error('start_date', 'Já existe uma folha de ponto para esta data.')
            return self.form_invalid(form)
        return super().form_valid(form)

class TimesheetDeleteView(LoginRequiredMixin, DeleteView):
    model = Timesheet
    success_url = reverse_lazy('timesheet:timesheet_list')
    
    def get_queryset(self):
        return Timesheet.objects.filter(user=self.request.user)

class TimesheetDetailView(LoginRequiredMixin, ListView): # Using ListView to list entries, but context will be the timesheet
    model = TimeEntry
    template_name = 'timesheet/timesheet_detail.html'
    context_object_name = 'entries'

    def _assignable_projects(self, user):
        return Project.objects.filter(
            status__in=[Project.Status.PLANNED, Project.Status.IN_PROGRESS, Project.Status.LATE]
        ).filter(
            Q(team=user) |
            Q(project_manager=user) |
            Q(project_owner=user)
        ).distinct()

    def get_queryset(self):
        timesheet = self.get_timesheet()
        user = self.request.user
        qs = TimeEntry.objects.filter(timesheet=timesheet)
        if user.role == getattr(user, 'Role', None).MANAGER and not (user.has_perm('timesheet.view_timesheet') or user.has_perm('timesheet.change_timesheet') or user.is_superuser):
            if user != timesheet.user:
                qs = qs.filter(project__project_manager=user)
        return qs

    def get_timesheet(self):
        qs = Timesheet.objects.all()
        user = self.request.user
        if user.role == getattr(user, 'Role', None).MANAGER and not (user.has_perm('timesheet.view_timesheet') or user.has_perm('timesheet.change_timesheet') or user.is_superuser):
            qs = qs.filter(Q(entries__project__project_manager=user) | Q(user=user)).distinct()
        elif not (user.has_perm('timesheet.view_timesheet') or user.has_perm('timesheet.change_timesheet') or user.is_superuser):
            qs = qs.filter(user=user)
        return get_object_or_404(qs, pk=self.kwargs['pk'])

    def _can_approve(self, user, timesheet):
        if user == timesheet.user:
            return False
        if user.is_superuser or user.has_perm('timesheet.change_timesheet'):
            return timesheet.status in [Timesheet.Status.SUBMITTED, Timesheet.Status.PARTIALLY_APPROVED]
        if user.role == getattr(user, 'Role', None).MANAGER:
            return timesheet.status in [Timesheet.Status.SUBMITTED, Timesheet.Status.PARTIALLY_APPROVED] and timesheet.entries.filter(project__project_manager=user).exists()
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        timesheet = self.get_timesheet()
        context['timesheet'] = timesheet
        context['is_editable'] = timesheet.status in [Timesheet.Status.DRAFT, Timesheet.Status.REJECTED]
        context['can_approve'] = self._can_approve(self.request.user, timesheet)
        
        # Generate days of the week
        days = []
        current_date = timesheet.start_date
        while current_date <= timesheet.end_date:
            days.append(current_date)
            current_date += timedelta(days=1)
        context['days'] = days
        
        # Context for Add Row Modal
        # Filter projects:
        # 1. Status must be IN_PROGRESS or LATE (active for timesheets)
        # 2. User must be in the team OR be the project manager OR be the project owner
        from django.db.models import Q
        context['projects'] = self._assignable_projects(self.request.user)
        context['tasks'] = Task.objects.all() # You might want to filter tasks based on project via AJAX later
        context['activities'] = Activity.objects.filter(active=True)

        # Group entries by Project/Task/Activity for the grid
        rows = {} # Key: (project_id, task_id, activity_id) -> {day: hours}
        for entry in context['entries']:
            key = (entry.project, entry.task, entry.activity)
            if key not in rows:
                rows[key] = {'project': entry.project, 'task': entry.task, 'activity': entry.activity, 'days': {}}
            rows[key]['days'][entry.date] = entry.hours
            
        # Convert rows to a list with ordered daily hours
        grid_rows = []
        for key, data in rows.items():
            daily_data = [] # Changed to list of dicts to include date for input name
            total_hours = 0
            for day in days:
                hours = data['days'].get(day, 0) # Default to 0 for calculation
                daily_data.append({'date': day, 'hours': hours if hours != 0 else ''})
                total_hours += float(hours) if hours else 0
            
            grid_rows.append({
                'project': data['project'],
                'task': data['task'],
                'activity': data['activity'],
                'daily_data': daily_data,
                'total_hours': total_hours
            })
            
        context['grid_rows'] = grid_rows
        
        # Calculate total hours for the entire timesheet
        total_timesheet_hours = sum(row['total_hours'] for row in grid_rows)
        context['total_timesheet_hours'] = total_timesheet_hours
        
        return context

class TimesheetActionView(LoginRequiredMixin, UpdateView):
    model = Timesheet
    fields = []
    template_name = 'timesheet/timesheet_detail.html' # Fallback

    def _assignable_projects(self, user):
        return Project.objects.filter(
            status__in=[Project.Status.PLANNED, Project.Status.IN_PROGRESS, Project.Status.LATE]
        ).filter(
            Q(team=user) |
            Q(project_manager=user) |
            Q(project_owner=user)
        ).distinct()
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == getattr(user, 'Role', None).MANAGER and not (user.has_perm('timesheet.change_timesheet') or user.is_superuser):
            qs = qs.filter(Q(entries__project__project_manager=user) | Q(user=user)).distinct()
        elif not (user.has_perm('timesheet.change_timesheet') or user.is_superuser):
            qs = qs.filter(user=user)
        return qs

    def post(self, request, *args, **kwargs):
        timesheet = self.get_object()
        action = request.POST.get('action')
        allowed_project_ids = set(self._assignable_projects(request.user).values_list('id', flat=True))
        
        print(f"DEBUG: TimesheetActionView.post called. Action: {action}, User: {request.user}")
        print(f"DEBUG: Entries BEFORE: {TimeEntry.objects.filter(timesheet=timesheet).count()}")
        print(f"DEBUG: POST keys: {list(request.POST.keys())}")

        # Only owner or privileged users can operate on a timesheet
        manager_scope = timesheet.entries.filter(project__project_manager=request.user).exists()
        if not (request.user == timesheet.user or request.user.has_perm('timesheet.change_timesheet') or request.user.is_superuser or (request.user.role == getattr(request.user, 'Role', None).MANAGER and manager_scope)):
            return redirect('timesheet:timesheet_list')
        is_editable = timesheet.status in [Timesheet.Status.DRAFT, Timesheet.Status.REJECTED]
        
        if action == 'submit':
            # Validate if timesheet has hours
            total_hours = timesheet.entries.aggregate(total=models.Sum('hours'))['total'] or 0
            if total_hours == 0:
                messages.error(request, 'Não é possível enviar uma folha de ponto sem horas lançadas.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
                
            timesheet.status = Timesheet.Status.SUBMITTED
            timesheet.partial_approvers.clear()
            timesheet.approved_by = None
            timesheet.save()
        elif action == 'approve':
            if timesheet.user == request.user:
                messages.error(request, 'Você não pode aprovar a própria folha. Solicite a aprovação de outro usuário.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            is_manager = request.user.role == getattr(request.user, 'Role', None).MANAGER
            has_scope = timesheet.entries.filter(project__project_manager=request.user).exists()
            if is_manager and not has_scope and not (request.user.has_perm('timesheet.change_timesheet') or request.user.is_superuser):
                messages.error(request, 'Você não tem permissão para aprovar esta folha.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)

            if request.user.has_perm('timesheet.change_timesheet') or request.user.is_superuser:
                timesheet.status = Timesheet.Status.APPROVED
                timesheet.approved_by = request.user
                timesheet.partial_approvers.clear()
                timesheet.save()
            elif is_manager and has_scope:
                # Register partial approval
                timesheet.partial_approvers.add(request.user)
                all_managers = set(
                    timesheet.entries.exclude(project__project_manager__isnull=True).values_list('project__project_manager', flat=True)
                )
                approved_managers = set(timesheet.partial_approvers.values_list('id', flat=True))
                if all_managers and all_managers.issubset(approved_managers):
                    timesheet.status = Timesheet.Status.APPROVED
                    timesheet.approved_by = request.user
                else:
                    timesheet.status = Timesheet.Status.PARTIALLY_APPROVED
                timesheet.save()
            else:
                messages.error(request, 'Você não tem permissão para aprovar esta folha.')
        elif action == 'reject':
            if timesheet.user == request.user:
                messages.error(request, 'Você não pode rejeitar a própria folha. Solicite a aprovação de outro usuário.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            is_manager = request.user.role == getattr(request.user, 'Role', None).MANAGER
            has_scope = timesheet.entries.filter(project__project_manager=request.user).exists()
            if not (request.user.has_perm('timesheet.change_timesheet') or request.user.is_superuser or (is_manager and has_scope)):
                messages.error(request, 'Você não tem permissão para rejeitar esta folha.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)

            if request.user.role == getattr(request.user, 'Role', None).MANAGER or request.user.has_perm('timesheet.change_timesheet') or request.user.is_superuser:
                timesheet.status = Timesheet.Status.REJECTED
                timesheet.rejection_reason = request.POST.get('reason', '')
                timesheet.partial_approvers.clear()
                timesheet.approved_by = None
                timesheet.save()
            else:
                messages.error(request, 'Você não tem permissão para rejeitar esta folha.')
        elif action == 'cancel':
            if timesheet.status not in [Timesheet.Status.SUBMITTED, Timesheet.Status.PARTIALLY_APPROVED]:
                messages.error(request, 'Apenas folhas enviadas podem ser canceladas.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            if request.user != timesheet.user and not (request.user.has_perm('timesheet.change_timesheet') or request.user.is_superuser):
                messages.error(request, 'Você não tem permissão para cancelar esta folha.')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            timesheet.status = Timesheet.Status.DRAFT
            timesheet.approved_by = None
            timesheet.rejection_reason = ''
            timesheet.partial_approvers.clear()
            timesheet.save()
            messages.success(request, 'Envio cancelado. Folha retornou para rascunho.')
        elif action == 'add_row':
            if not is_editable:
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            project_id = request.POST.get('project')
            task_id = request.POST.get('task') or None
            activity_id = request.POST.get('activity')

            if project_id and int(project_id) not in allowed_project_ids:
                messages.error(request, 'Não é possível apontar horas para um projeto não elegível (completo ou sem acesso).')
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            
            # Create an initial entry for the start date to ensure the row appears
            TimeEntry.objects.create(
                timesheet=timesheet,
                project_id=project_id,
                task_id=task_id,
                activity_id=activity_id,
                date=timesheet.start_date,
                hours=0
            )
        elif action == 'delete_row':
            if not is_editable:
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            project_id = request.POST.get('project_id')
            task_id = request.POST.get('task_id') or None
            activity_id = request.POST.get('activity_id')
            
            # Delete all TimeEntry records for this combination
            TimeEntry.objects.filter(
                timesheet=timesheet,
                project_id=project_id,
                task_id=task_id,
                activity_id=activity_id
            ).delete()
        elif action == 'save_grid':
            if not is_editable:
                return redirect('timesheet:timesheet_detail', pk=timesheet.pk)
            
            from django.db import transaction
            import logging
            logger = logging.getLogger(__name__)

            with transaction.atomic():
                # 1. Parse and group data from POST
                # Structure: {(proj, task, act): {date: hours}}
                grid_data = defaultdict(dict)
                
                print(f"DEBUG: POST keys: {list(request.POST.keys())}")

                for key, value in request.POST.items():
                    if key.startswith('hours_'):
                        # Format: hours_{proj}_{task}_{act}_{date}
                        parts = key.split('_')
                        if len(parts) >= 5:
                            try:
                                project_id = int(parts[1])
                                
                                # Handle Task ID
                                raw_task = parts[2]
                                task_id = int(raw_task) if raw_task not in ('', 'None', 'None') and raw_task is not None else None
                                
                                # Handle Activity ID
                                raw_act = parts[3]
                                activity_id = int(raw_act) if raw_act not in ('', 'None', 'None') and raw_act is not None else None
                                
                                date_str = parts[4]
                                
                                # Parse hours
                                val_str = (value or '').replace(',', '.').strip()
                                hours = float(val_str) if val_str else 0.0
                                
                                print(f"DEBUG: Parsed {key} -> Proj: {project_id}, Task: {task_id}, Act: {activity_id}, Date: {date_str}, Hours: {hours}")
                                
                                grid_data[(project_id, task_id, activity_id)][date_str] = hours
                                
                            except (ValueError, TypeError) as e:
                                print(f"DEBUG: Error parsing grid key {key}: {e}")
                                logger.error(f"Error parsing grid key {key}: {e}")
                                continue

                # 2. Process each row
                for (proj_id, task_id, act_id), daily_data in grid_data.items():
                    if proj_id not in allowed_project_ids:
                        messages.error(request, 'Não é possível registrar horas em projeto não elegível (completo ou sem acesso).')
                        continue
                    # Ensure anchor entry exists (Start Date)
                    # We do this first to ensure the row is preserved even if all hours are 0
                    TimeEntry.objects.get_or_create(
                        timesheet=timesheet,
                        project_id=proj_id,
                        task_id=task_id,
                        activity_id=act_id,
                        date=timesheet.start_date,
                        defaults={'hours': 0}
                    )

                    # Update/Create entries for specific dates
                    for date_str, hours in daily_data.items():
                        # Remove duplicates for this specific cell if any exist (cleanup)
                        entries = TimeEntry.objects.filter(
                            timesheet=timesheet,
                            project_id=proj_id,
                            task_id=task_id,
                            activity_id=act_id,
                            date=date_str
                        )
                        if entries.count() > 1:
                            # Keep first, delete others
                            entries.exclude(pk=entries.first().pk).delete()
                        
                        try:
                            entry, created = TimeEntry.objects.update_or_create(
                                timesheet=timesheet,
                                project_id=proj_id,
                                task_id=task_id,
                                activity_id=act_id,
                                date=date_str,
                                defaults={'hours': hours}
                            )
                            print(f"DEBUG: Entry {'created' if created else 'updated'}: {entry.id}, date={entry.date}, hours={entry.hours}")
                        except Exception as e:
                            print(f"DEBUG: Error saving entry {date_str}: {e}")
                            logger.error(f"Error saving entry {date_str}: {e}")

            # Return JSON response for AJAX requests, redirect for form submissions
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'multipart/form-data':
                return JsonResponse({'status': 'success', 'message': 'Hours saved successfully'})

        return redirect('timesheet:timesheet_detail', pk=timesheet.pk)

class TimeEntryListView(LoginRequiredMixin, ListView):
    model = TimeEntry
    template_name = 'timesheet/timeentry_list.html'
    context_object_name = 'entries'
    paginate_by = 20

    def get_queryset(self):
        # Changed filter per suggestion
        return TimeEntry.objects.filter(timesheet__user=self.request.user)

class TimeEntryCreateView(LoginRequiredMixin, CreateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = 'timesheet/timeentry_form.html'
    success_url = reverse_lazy('timesheet:entry_list')

    def form_valid(self, form):
        return super().form_valid(form)

class TimeEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeEntry
    form_class = TimeEntryForm
    template_name = 'timesheet/timeentry_form.html'
    success_url = reverse_lazy('timesheet:entry_list')

    def get_queryset(self):
        # Only allow editing own entries via the timesheet relationship
        return TimeEntry.objects.filter(timesheet__user=self.request.user)


class ActivityPermissionMixin(PermissionRequiredMixin):
    permission_required = 'timesheet.change_activity'
    raise_exception = True


class ActivityListView(LoginRequiredMixin, ActivityPermissionMixin, ListView):
    model = Activity
    template_name = 'timesheet/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 25

    def get_queryset(self):
        return Activity.objects.all().order_by('name')


class ActivityCreateView(LoginRequiredMixin, ActivityPermissionMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'timesheet/activity_form.html'
    success_url = reverse_lazy('timesheet:activity_list')


class ActivityUpdateView(LoginRequiredMixin, ActivityPermissionMixin, UpdateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'timesheet/activity_form.html'
    success_url = reverse_lazy('timesheet:activity_list')


class ActivityDeleteView(LoginRequiredMixin, ActivityPermissionMixin, DeleteView):
    model = Activity
    template_name = 'timesheet/activity_confirm_delete.html'
    success_url = reverse_lazy('timesheet:activity_list')


class ReportsDashboardView(LoginRequiredMixin, PermissionRequiredMixin, generic.TemplateView):
    template_name = 'reports/dashboard.html'
    permission_required = 'core.access_reports'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filters
        params = self.request.GET
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        status_filter = params.get('status')

        def parse_date(val):
            try:
                return datetime.fromisoformat(val).date()
            except Exception:
                return None

        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        ts_qs = Timesheet.objects.all()
        te_qs = TimeEntry.objects.exclude(hours__isnull=True)

        if start_date:
            ts_qs = ts_qs.filter(start_date__gte=start_date)
            te_qs = te_qs.filter(date__gte=start_date)
        if end_date:
            ts_qs = ts_qs.filter(end_date__lte=end_date)
            te_qs = te_qs.filter(date__lte=end_date)
        if status_filter:
            ts_qs = ts_qs.filter(status=status_filter)

        status_data = list(
            ts_qs.values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )

        monthly_hours = list(
            te_qs
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('hours'))
            .order_by('month')
        )

        approvals = {
            'pending': ts_qs.filter(status=Timesheet.Status.SUBMITTED).count(),
            'partial': ts_qs.filter(status=Timesheet.Status.PARTIALLY_APPROVED).count(),
            'approved': ts_qs.filter(status=Timesheet.Status.APPROVED).count(),
            'rejected': ts_qs.filter(status=Timesheet.Status.REJECTED).count(),
        }

        # KPIs
        total_ts = sum([row['total'] for row in status_data]) if status_data else 0
        hours_total = te_qs.aggregate(total=Sum('hours'))['total'] or 0
        months_count = len(monthly_hours) or 1
        avg_hours_per_month = hours_total / months_count if months_count else 0

        top_users = list(
            te_qs
            .values('timesheet__user__username')
            .annotate(total=Sum('hours'))
            .order_by('-total')[:5]
        )

        context.update({
            'status_data': json.dumps(status_data, default=str),
            'monthly_hours': json.dumps(monthly_hours, default=str),
            'approvals': approvals,
            'kpis': {
                'total_ts': total_ts,
                'pending': approvals['pending'],
                'partial': approvals['partial'],
                'approved': approvals['approved'],
                'rejected': approvals['rejected'],
                'hours_total': float(hours_total),
                'avg_hours_per_month': float(avg_hours_per_month),
            },
            'top_users': json.dumps(top_users, default=str),
            'filters': {
                'start_date': start_date.isoformat() if start_date else '',
                'end_date': end_date.isoformat() if end_date else '',
                'status': status_filter or '',
            }
        })
        return context


class ReportsExportView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'core.access_reports'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        fmt = request.GET.get('format', 'csv').lower()
        queryset = Timesheet.objects.select_related('user', 'approved_by')
        rows = []
        for ts in queryset:
            rows.append([
                ts.id,
                ts.user.username,
                ts.start_date,
                ts.end_date,
                ts.status,
                ts.approved_by.username if ts.approved_by else '',
                ts.created_at,
                ts.updated_at,
            ])

        if fmt == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="reports_timesheets.csv"'
            writer = csv.writer(response)
            writer.writerow(['ID', 'Usuário', 'Início', 'Fim', 'Status', 'Aprovado por', 'Criado em', 'Atualizado em'])
            writer.writerows(rows)
            return response

        if fmt == 'xlsx' and openpyxl:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['ID', 'Usuário', 'Início', 'Fim', 'Status', 'Aprovado por', 'Criado em', 'Atualizado em'])
            for r in rows:
                ws.append(r)
            stream = BytesIO()
            wb.save(stream)
            response = HttpResponse(stream.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="reports_timesheets.xlsx"'
            return response

        if fmt == 'pdf' and canvas and letter:
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.setTitle('Relatório de Timesheets')
            p.drawString(50, 750, 'Relatório de Timesheets')
            p.drawString(50, 730, f'Total registros: {len(rows)}')
            y = 700
            for r in rows[:40]:
                line = f"ID {r[0]} | {r[1]} | {r[2]} -> {r[3]} | {r[4]}"
                p.drawString(50, y, line)
                y -= 15
                if y < 50:
                    p.showPage()
                    y = 750
            p.save()
            pdf = buffer.getvalue()
            buffer.close()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reports_timesheets.pdf"'
            return response

        return HttpResponse('Formato não suportado ou dependência ausente.', status=400)
