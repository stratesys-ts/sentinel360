from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, path
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib import messages
import secrets

from .models import GroupModuleAccess, User
from .forms import InternalUserPasswordForm

class CustomUserAdmin(UserAdmin):
    """Admin base para o modelo de usuário (não registrada para esconder o menu genérico)."""
    fieldsets = (
        (_('Credenciais'), {'fields': ('username', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name', 'email', 'codigo_tr', 'employment_modality')}),
        (_('Papel e projeto'), {'fields': ('role', 'client_project')}),
        (
            _('Permissões'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'role',
                    'client_project',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                ),
            },
        ),
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'client_project',
        'is_staff',
        'is_active',
    )
    list_filter = ('role', 'client_project', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    list_select_related = ('client_project',)
    autocomplete_fields = ('client_project',)

    class Media:
        css = {
            'all': ('css/admin_internaluser.css',)
        }
        js = ('js/admin_internaluser_password.js',)

from .models import InternalUser, ExternalUser

@admin.register(InternalUser)
class InternalUserAdmin(UserAdmin):
    actions = ['delete_selected']
    fieldsets = (
        (_('Credenciais'), {'fields': ('username', 'new_password', 'confirm_password', 'generate_password', 'force_password_change')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name', 'email', 'codigo_tr', 'employment_modality')}),
        (_('Papel'), {'fields': ('role',)}),
        (
            _('Permissões'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    form = InternalUserPasswordForm
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'role',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                ),
            },
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    class Media:
        css = {
            'all': ('css/admin_internaluser.css',)
        }
        js = ('js/admin_internaluser_password.js',)

    def save_model(self, request, obj, form, change):
        pwd = form.cleaned_data.get('new_password')
        generate = form.cleaned_data.get('generate_password')
        if generate:
            pwd = secrets.token_urlsafe(12)
            obj.set_password(pwd)
            messages.info(request, _("Senha gerada automaticamente."))
        elif pwd:
            obj.set_password(pwd)
        obj.force_password_change = form.cleaned_data.get('force_password_change') or False
        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ('codigo_tr', 'employment_modality') and formfield:
            formfield.help_text = ''
        return formfield

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(role=User.Role.CLIENT)

    @admin.display(description="Excluir")
    def delete_link(self, obj):
        url = reverse('admin:core_internaluser_delete', args=[obj.pk])
        return format_html('<a class="text-danger" href="{}">Excluir</a>', url)

@admin.register(ExternalUser)
class ExternalUserAdmin(UserAdmin):
    actions = ['delete_selected']
    fieldsets = (
        (_('Credenciais'), {'fields': ('username', 'password')}),
        (_('Informações pessoais'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Projeto do cliente'), {'fields': ('client_project', 'role')}),
        (
            _('Permissões'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'client_project',
                    'role',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                ),
            },
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'client_project', 'is_active', 'delete_link')
    list_filter = ('client_project', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    list_select_related = ('client_project',)
    autocomplete_fields = ('client_project',)

    class Media:
        css = {
            'all': ('css/admin_internaluser.css',)
        }
        js = ('js/admin_internaluser_password.js',)

    @admin.display(description="Excluir")
    def delete_link(self, obj):
        url = reverse('admin:core_externaluser_delete', args=[obj.pk])
        return format_html('<a class="text-danger" href="{}">Excluir</a>', url)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=User.Role.CLIENT)

class GroupModuleAccessInline(admin.StackedInline):
    model = GroupModuleAccess
    can_delete = False
    extra = 0
    verbose_name = "Module visibility"
    verbose_name_plural = "Module visibility"
    fields = ('helpdesk', 'approvals', 'approvals_he', 'admin', 'reports')

class CustomGroupAdmin(GroupAdmin):
    list_display = ('name', 'module_access_summary')
    list_select_related = ('module_access',)
    list_filter = (
        'module_access__helpdesk',
        'module_access__approvals',
        'module_access__approvals_he',
        'module_access__admin',
        'module_access__reports',
    )
    inlines = [GroupModuleAccessInline]

    def get_inline_instances(self, request, obj=None):
        # Evita criar linha duplicada na criação de grupo.
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    @admin.display(description="Módulos liberados")
    def module_access_summary(self, obj):
        if not hasattr(obj, 'module_access'):
            return "-"

        modules = []
        if obj.module_access.helpdesk:
            modules.append("Helpdesk")
        if obj.module_access.approvals:
            modules.append("Aprovações")
        if getattr(obj.module_access, 'approvals_he', False):
            modules.append("Aprovação HE")
        if obj.module_access.admin:
            modules.append("Admin")
        if obj.module_access.reports:
            modules.append("Relatórios")
        return ", ".join(modules) if modules else "Nenhum"

# Re-register Group with inline for module visibility toggles
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)


@admin.register(GroupModuleAccess)
class GroupModuleAccessAdmin(admin.ModelAdmin):
    list_display = ('group', 'helpdesk', 'approvals', 'approvals_he', 'admin', 'reports')
    list_filter = ('helpdesk', 'approvals', 'approvals_he', 'admin', 'reports')
    search_fields = ('group__name',)
    list_select_related = ('group',)
    fields = ('group', 'helpdesk', 'approvals', 'approvals_he', 'admin', 'reports')
    autocomplete_fields = ('group',)
    ordering = ('group__name',)

class HiddenUserAdmin(CustomUserAdmin):
    """Mantém autocomplete no admin sem exibir o menu Users."""

    def get_model_perms(self, request):
        return {}

# Evita duplo registro em reloads
if User in admin.site._registry:
    admin.site.unregister(User)
admin.site.register(User, HiddenUserAdmin)
