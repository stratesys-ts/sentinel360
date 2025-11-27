import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q
from django.shortcuts import reverse
from django.utils import timezone

from apps.core.models import GroupModuleAccess

IGNORED_DIRS = {
    '.git',
    '.venv',
    'staticfiles',
    'media',
    'node_modules',
    '__pycache__',
}

WATCHED_RELATIVE_PATHS = (
    'apps',
    'templates',
    'static',
    'erp_core',
)


def module_access(request):
    user = getattr(request, 'user', None)
    flags = {
        'helpdesk': False,
        'approvals': False,
        'approvals_he': False,
        'admin': False,
        'reports': False,
    }

    if not user or not user.is_authenticated:
        return {'module_access': flags}

    if user.is_superuser:
        return {'module_access': {k: True for k in flags}}

    groups = user.groups.all()
    for g in groups:
        access = getattr(g, 'module_access', None)
        if not access:
            access = GroupModuleAccess.objects.get_or_create(group=g)[0]
        flags['helpdesk'] = flags['helpdesk'] or access.helpdesk
        flags['approvals'] = flags['approvals'] or access.approvals
        flags['approvals_he'] = flags['approvals_he'] or getattr(access, 'approvals_he', False)
        flags['admin'] = flags['admin'] or access.admin
        flags['reports'] = flags['reports'] or getattr(access, 'reports', False)

    if user.has_perm('core.access_helpdesk'):
        flags['helpdesk'] = True
    if user.has_perm('core.access_approvals'):
        flags['approvals'] = True
    if user.has_perm('core.access_approvals_he'):
        flags['approvals_he'] = True
    if user.has_perm('core.access_admin'):
        flags['admin'] = True
    if user.has_perm('core.access_reports'):
        flags['reports'] = True

    return {'module_access': flags}


def _watched_paths() -> Iterator[Path]:
    base = settings.BASE_DIR
    yield base
    for rel in WATCHED_RELATIVE_PATHS:
        candidate = base / rel
        if candidate.exists():
            yield candidate


def _latest_filesystem_timestamp() -> Optional[datetime]:
    latest_ts: float = 0.0
    for path in _watched_paths():
        if path.is_file():
            try:
                latest_ts = max(latest_ts, path.stat().st_mtime)
            except OSError:
                continue
            continue

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for name in files:
                if name.startswith('.'):
                    continue
                full_path = Path(root) / name
                try:
                    latest_ts = max(latest_ts, full_path.stat().st_mtime)
                except OSError:
                    continue

    if latest_ts <= 0:
        return None

    tz = timezone.get_default_timezone()
    return datetime.fromtimestamp(latest_ts, tz)


def _alert_notifications(request):
    from apps.projects.models import Issue
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return []

    now = timezone.now()
    near_due = now + timedelta(days=10)

    ticket_qs = Issue.objects.filter(
        issue_type=Issue.IssueType.HELP_DESK
    ).filter(
        Q(status=Issue.Status.TODO) |
        Q(status=Issue.Status.DOING) |
        Q(due_date__range=(now.date(), near_due.date()))
    ).order_by('-status', 'due_date')[:4]

    task_qs = Issue.objects.filter(
        issue_type=Issue.IssueType.TASK
    ).filter(
        Q(status=Issue.Status.TODO) |
        Q(due_date__range=(now.date(), near_due.date()))
    ).order_by('due_date')[:4]

    alerts = []
    redirect_to = reverse('core:dashboard')
    query = urlencode({'redirect_to': redirect_to})
    for ticket in ticket_qs:
        alerts.append({
            'type': 'ticket',
            'label': ticket.title,
            'subtitle': f"Chamado #{ticket.public_id or ticket.id}",
            'url': f"{reverse('helpdesk:ticket_update', kwargs={'pk': ticket.pk})}?{query}",
        })

    for task in task_qs:
        alerts.append({
            'type': 'task',
            'label': task.title,
            'subtitle': f"Tarefa #{task.public_id or task.id}",
            'url': f"{reverse('projects:task_edit', kwargs={'pk': task.pk})}?{query}",
        })

    return alerts


def admin_last_update(request):
    if not request.path.startswith('/admin'):
        return {}

    last_update = _latest_filesystem_timestamp()
    return {'admin_last_update': last_update}


def alert_notifications(request):
    return {'alert_notifications': _alert_notifications(request)}
