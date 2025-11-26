from django.urls import path
from django.urls import path
from .views import (
    TimeEntryListView, TimeEntryCreateView, TimeEntryUpdateView,
    TimesheetListView, TimesheetCreateView, TimesheetDetailView, TimesheetActionView,
    TimesheetDeleteView, TimesheetApprovalListView,
    ReportsDashboardView, ReportsExportView,
    ActivityListView, ActivityCreateView, ActivityUpdateView, ActivityDeleteView
)

app_name = 'timesheet'

urlpatterns = [
    path('', TimesheetListView.as_view(), name='timesheet_list'),
    path('approvals/', TimesheetApprovalListView.as_view(), name='timesheet_approval_list'),
    path(
        'approvals/he/',
        TimesheetApprovalListView.as_view(template_name='timesheet/timesheet_approval_he_list.html'),
        name='timesheet_approval_he_list'
    ),
    path('entries/', TimeEntryListView.as_view(), name='entry_list'),
    path('create/', TimesheetCreateView.as_view(), name='timesheet_create'),
    path('delete/<int:pk>/', TimesheetDeleteView.as_view(), name='timesheet_delete'),
    path('<int:pk>/', TimesheetDetailView.as_view(), name='timesheet_detail'),
    path('<int:pk>/action/', TimesheetActionView.as_view(), name='timesheet_action'),
    path('entries/add/', TimeEntryCreateView.as_view(), name='entry_create'),
    path('entries/<int:pk>/edit/', TimeEntryUpdateView.as_view(), name='entry_edit'),
    path('reports/', ReportsDashboardView.as_view(), name='reports_dashboard'),
    path('reports/export/', ReportsExportView.as_view(), name='reports_export'),
    path('activities/', ActivityListView.as_view(), name='activity_list'),
    path('activities/add/', ActivityCreateView.as_view(), name='activity_create'),
    path('activities/<int:pk>/edit/', ActivityUpdateView.as_view(), name='activity_update'),
    path('activities/<int:pk>/delete/', ActivityDeleteView.as_view(), name='activity_delete'),
]
