from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from apps.core.models import GroupModuleAccess, _sync_perms_from_flags


class Command(BaseCommand):
    help = "Sincroniza flags de módulo (GroupModuleAccess) a partir das permissões e vice-versa."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Sincronizando flags a partir das permissões..."))

        perm_map = {
            'access_helpdesk': 'helpdesk',
            'access_approvals': 'approvals',
            'access_approvals_he': 'approvals_he',
            'access_admin': 'admin',
            'access_reports': 'reports',
        }

        for gma in GroupModuleAccess.objects.select_related('group'):
            group_perms = set(gma.group.permissions.values_list('codename', flat=True))
            # Atualiza flags com base nas permissões atuais
            for perm_code, flag in perm_map.items():
                setattr(gma, flag, perm_code in group_perms)
            gma.save()
            _sync_perms_from_flags(gma)
            self.stdout.write(f" - {gma.group.name}: {', '.join([f for f in perm_map.values() if getattr(gma, f)]) or 'nenhum'}")

        self.stdout.write(self.style.SUCCESS("Concluído. Flags e permissões sincronizadas."))
