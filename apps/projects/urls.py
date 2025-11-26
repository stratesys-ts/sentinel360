from django.urls import path
from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectUpdateView,
    ProjectDeleteView,
    TaskUpdateView,
    ProjectHoursView,
    ProjectTasksView,
    ProjectKanbanView,
    ProjectRisksView,
    QuickTaskCreateView,
    TaskAssignedListView,
    IssueDetailView,
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    path('create/', ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/tasks/', ProjectTasksView.as_view(), name='project_tasks'),
    path('<int:pk>/kanban/', ProjectKanbanView.as_view(), name='project_kanban'),
    path('<int:pk>/risks/', ProjectRisksView.as_view(), name='project_risks'),
    path('<int:pk>/hours/', ProjectHoursView.as_view(), name='project_hours'),
    path('<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_update'),
    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('task/<int:pk>/', IssueDetailView.as_view(), name='task_detail'),
    path('issues/<int:pk>/', IssueDetailView.as_view(), name='issue_detail'),
    path('task/<int:pk>/update/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/new/', QuickTaskCreateView.as_view(), name='task_quick_create'),
    path('tasks/', TaskAssignedListView.as_view(), name='task_list_assigned'),
]
