import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.helpdesk.models import Category, Ticket
from apps.projects.models import Project, Task
from apps.timesheet.models import TimeEntry

User = get_user_model()

def create_demo_data():
    print("Creating demo data...")

    # Users
    admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@erp.com', 'role': 'ADMIN', 'is_staff': True, 'is_superuser': True})
    admin.set_password('admin')
    admin.save()

    manager, _ = User.objects.get_or_create(username='manager', defaults={'email': 'manager@erp.com', 'role': 'MANAGER'})
    manager.set_password('manager')
    manager.save()

    collab, _ = User.objects.get_or_create(username='collab', defaults={'email': 'collab@erp.com', 'role': 'COLLABORATOR'})
    collab.set_password('collab')
    collab.save()

    client, _ = User.objects.get_or_create(username='client', defaults={'email': 'client@erp.com', 'role': 'CLIENT'})
    client.set_password('client')
    client.save()

    print("Users created.")

    # Help Desk
    cat_hardware, _ = Category.objects.get_or_create(name='Hardware', sla_hours=24)
    cat_software, _ = Category.objects.get_or_create(name='Software', sla_hours=8)

    Ticket.objects.get_or_create(
        title='Computador lento',
        defaults={
            'description': 'Meu computador está demorando muito para ligar.',
            'priority': 'MEDIUM',
            'category': cat_hardware,
            'created_by': client,
            'status': 'OPEN'
        }
    )
    
    Ticket.objects.get_or_create(
        title='Erro no sistema',
        defaults={
            'description': 'Não consigo acessar o módulo financeiro.',
            'priority': 'HIGH',
            'category': cat_software,
            'created_by': client,
            'assigned_to': collab,
            'status': 'IN_PROGRESS'
        }
    )

    print("Help Desk data created.")

    # Projects
    proj, _ = Project.objects.get_or_create(
        name='Website Institucional',
        defaults={
            'client': client,
            'description': 'Desenvolvimento do novo site da empresa.',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
            'status': 'IN_PROGRESS',
            'budget': 15000.00
        }
    )
    proj.team.add(manager, collab)

    Task.objects.get_or_create(
        title='Design da Home',
        project=proj,
        defaults={'assigned_to': collab, 'status': 'DONE', 'priority': 'HIGH', 'due_date': date.today() + timedelta(days=5)}
    )
    
    Task.objects.get_or_create(
        title='Desenvolvimento Frontend',
        project=proj,
        defaults={'assigned_to': collab, 'status': 'DOING', 'priority': 'MEDIUM', 'due_date': date.today() + timedelta(days=15)}
    )

    print("Project data created.")

    # Timesheet
    TimeEntry.objects.get_or_create(
        user=collab,
        date=date.today(),
        start_time='09:00',
        defaults={
            'end_time': '18:00',
            'pause_duration': timedelta(hours=1),
            'description': 'Trabalho no frontend do site.',
            'is_approved': False
        }
    )

    print("Timesheet data created.")
    print("Done!")

if __name__ == '__main__':
    create_demo_data()
