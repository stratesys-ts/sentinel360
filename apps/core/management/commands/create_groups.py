from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Creates default user groups'

    def handle(self, *args, **kwargs):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        from apps.projects.models import Project, Task
        from apps.timesheet.models import TimeEntry
        from apps.helpdesk.models import Ticket

        groups_permissions = {
            'Administrador': '__all__',
            'Gerente Delivery': {
                '__modules__': ['access_helpdesk', 'access_approvals'],
                'projects': ['view_project', 'add_project', 'change_project', 'delete_project'],
                'tasks': ['view_task', 'add_task', 'change_task', 'delete_task'],
                'timesheet': ['view_timeentry', 'change_timeentry', 'delete_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket'],
            },
            'Gerente AMS': {
                '__modules__': ['access_helpdesk', 'access_approvals'],
                'projects': ['view_project', 'add_project', 'change_project', 'delete_project'],
                'tasks': ['view_task', 'add_task', 'change_task', 'delete_task'],
                'timesheet': ['view_timeentry', 'change_timeentry', 'delete_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket'],
            },
            'Gerente Orion': {
                '__modules__': ['access_helpdesk', 'access_approvals'],
                'projects': ['view_project', 'add_project', 'change_project', 'delete_project'],
                'tasks': ['view_task', 'add_task', 'change_task', 'delete_task'],
                'timesheet': ['view_timeentry', 'change_timeentry', 'delete_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket'],
            },
            'Consultor Delivery': {
                '__modules__': ['access_helpdesk'],
                'projects': ['view_project'],
                'tasks': ['view_task', 'change_task'],
                'timesheet': ['view_timeentry', 'add_timeentry', 'change_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket'],
            },
            'Consultor AMS': {
                '__modules__': ['access_helpdesk'],
                'projects': ['view_project'],
                'tasks': ['view_task', 'change_task'],
                'timesheet': ['view_timeentry', 'add_timeentry', 'change_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket'],
            },
            'Consultor Orion': {
                '__modules__': ['access_helpdesk'],
                'projects': ['view_project'],
                'tasks': ['view_task', 'change_task'],
                'timesheet': ['view_timeentry', 'add_timeentry', 'change_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket'],
            },
            'Cliente externo': {
                '__modules__': ['access_helpdesk'],
                'projects': ['view_project'],
                'helpdesk': ['view_ticket', 'add_ticket'],
            },
            'Recursos Humanos': {
                '__modules__': ['access_helpdesk', 'access_reports'],
            },
            'Gerente de Projetos Delivery': { # Assuming similar to Gerente Delivery for now
                 '__modules__': ['access_helpdesk', 'access_approvals'],
                 'projects': ['view_project', 'add_project', 'change_project', 'delete_project'],
                'tasks': ['view_task', 'add_task', 'change_task', 'delete_task'],
                'timesheet': ['view_timeentry', 'change_timeentry', 'delete_timeentry'],
                'helpdesk': ['view_ticket', 'add_ticket', 'change_ticket', 'delete_ticket'],
            }
        }

        for group_name, permissions_map in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Group "{group_name}" created'))
            else:
                self.stdout.write(f'Group "{group_name}" updated')

            if permissions_map == '__all__':
                # Administrador gets full access (including module flags)
                group.permissions.set(Permission.objects.all())
                self.stdout.write('  - Assigned ALL permissions to Administrador')
            else:
                # Always clear and rebuild permissions so the command is idempotent
                group.permissions.clear()

                # Module-level flags (custom permissions declared in User Meta)
                module_flags = permissions_map.pop('__modules__', [])
                for codename in module_flags:
                    try:
                        permission = Permission.objects.get(codename=codename)
                        group.permissions.add(permission)
                        self.stdout.write(f'  - Added module flag {codename} to {group_name}')
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'  - Module flag {codename} not found'))

                for app_label, perms in permissions_map.items():
                    for codename in perms:
                        try:
                            permission = Permission.objects.get(codename=codename)
                            group.permissions.add(permission)
                            self.stdout.write(f'  - Added {codename} to {group_name}')
                        except Permission.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f'  - Permission {codename} not found'))

            # Atualiza flags de module_access alinhadas às permissões de módulo
            if hasattr(group, 'module_access'):
                gma = group.module_access
            else:
                from apps.core.models import GroupModuleAccess
                gma, _ = GroupModuleAccess.objects.get_or_create(group=group)
            module_perms = set(group.permissions.values_list('codename', flat=True))
            gma.helpdesk = 'access_helpdesk' in module_perms
            gma.approvals = 'access_approvals' in module_perms
            gma.approvals_he = 'access_approvals_he' in module_perms
            gma.admin = 'access_admin' in module_perms
            gma.reports = 'access_reports' in module_perms
            gma.save()
            self.stdout.write(f'  - Module flags saved for {group_name}')
