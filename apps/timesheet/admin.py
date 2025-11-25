from django.contrib import admin
from django.db.models import Sum
from unfold.admin import ModelAdmin

from .models import Activity, TimeEntry, Timesheet

@admin.register(Activity)
class ActivityAdmin(ModelAdmin):
    list_display = ('name', 'active')
    list_filter = ('active',)
    search_fields = ('name',)
    list_editable = ('active',)
    ordering = ('name',)

@admin.register(Timesheet)
class TimesheetAdmin(ModelAdmin):
    list_display = ('user', 'period', 'status', 'approved_by', 'total_hours')
    list_filter = ('status', 'user', 'approved_by', 'start_date')
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'approved_by__username',
    )
    autocomplete_fields = ('user', 'approved_by', 'partial_approvers')
    filter_horizontal = ('partial_approvers',)
    list_select_related = ('user', 'approved_by')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('user', 'approved_by').prefetch_related('partial_approvers')
        return qs.annotate(total_hours=Sum('entries__hours'))

    @admin.display(description='Período', ordering='start_date')
    def period(self, obj):
        return f"{obj.start_date:%d/%m/%Y} - {obj.end_date:%d/%m/%Y}"

    @admin.display(description='Horas')
    def total_hours(self, obj):
        return obj.total_hours or 0

@admin.register(TimeEntry)
class TimeEntryAdmin(ModelAdmin):
    list_display = ('get_user', 'date', 'project', 'task', 'activity', 'hours')
    list_filter = ('timesheet__user', 'date', 'project', 'activity')
    search_fields = ('timesheet__user__username', 'description', 'project__name', 'task__title')
    autocomplete_fields = ('timesheet', 'project', 'task', 'activity')
    list_select_related = ('timesheet', 'project', 'task', 'activity', 'timesheet__user')
    date_hierarchy = 'date'
    ordering = ('-date',)
    list_per_page = 50
    
    @admin.display(description='Usuário', ordering='timesheet__user__username')
    def get_user(self, obj):
        if obj.timesheet and obj.timesheet.user:
            user = obj.timesheet.user
            return user.get_full_name() or user.username
        return "Sem timesheet"
