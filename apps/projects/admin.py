from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CostCenter, Project, Issue

@admin.register(CostCenter)
class CostCenterAdmin(ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = (
        'name',
        'client',
        'project_manager',
        'status',
        'start_date',
        'end_date',
        'external_access',
        'geography',
    )
    list_filter = (
        'status',
        'external_access',
        'currency',
        'geography',
        'industry',
        'project_manager',
        'client',
    )
    search_fields = (
        'name',
        'description',
        'client__username',
        'project_manager__username',
        'project_owner__username',
    )
    autocomplete_fields = ('client', 'project_manager', 'project_owner', 'cost_center', 'team')
    list_select_related = ('client', 'project_manager', 'project_owner', 'cost_center')
    ordering = ('name',)
    date_hierarchy = 'start_date'
    list_per_page = 25

@admin.register(Issue)
class IssueAdmin(ModelAdmin):
    list_display = ('title', 'issue_type', 'project', 'assigned_to', 'colleague', 'status', 'priority', 'due_date')
    list_filter = ('issue_type', 'status', 'priority', 'project', 'assigned_to', 'colleague')
    search_fields = ('title', 'description', 'project__name', 'assigned_to__username', 'colleague__username')
    autocomplete_fields = ('project', 'assigned_to', 'colleague', 'created_by')
    list_select_related = ('project', 'assigned_to', 'colleague', 'created_by')
    date_hierarchy = 'due_date'
    ordering = ('-due_date', 'title')
    list_per_page = 50
