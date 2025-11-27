from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        MANAGER = 'MANAGER', _('Manager')
        COLLABORATOR = 'COLLABORATOR', _('Collaborator')
        CLIENT = 'CLIENT', _('Client')

    employment_modality = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Modalidade de Contratação'),
        help_text=_('Modalidade de contratação do usuário.')
    )
    codigo_tr = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Código TR'),
        help_text=_('Identificador de TR vinculado ao recurso.')
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COLLABORATOR,
        verbose_name=_('Role')
    )
    
    client_project = models.ForeignKey(
        'projects.Project', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='client_users',
        verbose_name=_('Client Project'),
        help_text=_('Project this client user is restricted to.')
    )

    def is_manager(self):
        return self.role == self.Role.MANAGER or self.is_superuser

    def is_client(self):
        return self.role == self.Role.CLIENT

    def is_collaborator(self):
        return self.role == self.Role.COLLABORATOR

    force_password_change = models.BooleanField(
        default=False,
        verbose_name=_('Forçar alteração de senha'),
        help_text=_('Exigir atualização da senha no próximo login.')
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = [
            ('access_helpdesk', _('Can access Helpdesk module')),
            ('access_approvals', _('Can access Approvals module')),
            ('access_approvals_he', _('Can access HE Approvals module')),
            ('access_admin', _('Can access Administration module')),
            ('access_reports', _('Can access Reports module')),
        ]

class InternalUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().exclude(role=User.Role.CLIENT)

class InternalUser(User):
    objects = InternalUserManager()
    class Meta:
        proxy = True
        verbose_name = _('Usuário interno')
        verbose_name_plural = _('Usuários internos')

class ExternalUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(role=User.Role.CLIENT)

class ExternalUser(User):
    objects = ExternalUserManager()
    class Meta:
        proxy = True
        verbose_name = _('Usuário externo')
        verbose_name_plural = _('Usuários externos')

class GroupModuleAccess(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='module_access')
    helpdesk = models.BooleanField(default=False)
    approvals = models.BooleanField(default=False)
    approvals_he = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    reports = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Visibilidade de módulos do grupo')
        verbose_name_plural = _('Visibilidade de módulos do grupo')

    def __str__(self):
        return f"Module access for {self.group.name}"

@receiver(post_save, sender=Group)
def ensure_module_access(sender, instance, created, **kwargs):
    if created:
        GroupModuleAccess.objects.create(group=instance)


def _sync_perms_from_flags(gma: GroupModuleAccess):
    """Add/remove module permissions based on flags to avoid stale access when hiding menus."""
    flag_to_perm = {
        'helpdesk': 'access_helpdesk',
        'approvals': 'access_approvals',
        'approvals_he': 'access_approvals_he',
        'admin': 'access_admin',
        'reports': 'access_reports',
    }
    for flag, code in flag_to_perm.items():
        try:
            perm = Permission.objects.get(codename=code)
        except Permission.DoesNotExist:
            continue
        has_flag = getattr(gma, flag)
        if has_flag:
            gma.group.permissions.add(perm)
        else:
            gma.group.permissions.remove(perm)


@receiver(post_save, sender=GroupModuleAccess)
def sync_group_permissions(sender, instance, **kwargs):
    _sync_perms_from_flags(instance)
