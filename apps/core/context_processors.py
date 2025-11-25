from apps.core.models import GroupModuleAccess


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

    # Superuser sees everything
    if user.is_superuser:
        return {'module_access': {k: True for k in flags}}

    groups = user.groups.all()
    for g in groups:
        access = getattr(g, 'module_access', None)
        if not access:
            # auto-create if missing
            access = GroupModuleAccess.objects.get_or_create(group=g)[0]
        flags['helpdesk'] = flags['helpdesk'] or access.helpdesk
        flags['approvals'] = flags['approvals'] or access.approvals
        flags['approvals_he'] = flags['approvals_he'] or getattr(access, 'approvals_he', False)
        flags['admin'] = flags['admin'] or access.admin
        flags['reports'] = flags['reports'] or getattr(access, 'reports', False)

    # Reforça flags com permissões reais (evita menu sem permissão)
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
