from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.timesheet.models import Timesheet, TimeEntry
from apps.projects.models import Project, Issue

User = get_user_model()

def create_test_data():
    user, created = User.objects.get_or_create(username='testuser', defaults={
        'email': 'testuser@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'role': User.Role.COLLABORATOR,
    })
    if created:
        user.set_password('123456')
        user.save()
    
    today = timezone.now().date()
    first_day_this_month = today.replace(day=1)
    first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)

    # Criar folhas de ponto para este mês e mês passado
    ts1, created = Timesheet.objects.get_or_create(user=user, start_date=first_day_this_month, defaults={
        'end_date': first_day_this_month + timedelta(days=6),
        'status': Timesheet.Status.DRAFT
    })

    ts2, created = Timesheet.objects.get_or_create(user=user, start_date=first_day_last_month, defaults={
        'end_date': first_day_last_month + timedelta(days=6),
        'status': Timesheet.Status.APPROVED
    })

    # Usar projetos e tarefas existentes (pegar o primeiro se houver)
    project = Project.objects.first()
    task = Issue.objects.filter(project=project).first() if project else None

    # Criar entradas de tempo para a folha
    for day in range(7):
        date = ts1.start_date + timedelta(days=day)
        if project:
            TimeEntry.objects.get_or_create(timesheet=ts1, project=project, task=task, date=date, defaults={
                'hours': 4,
                'description': 'Projeto de teste'
            })

    print('Dados de teste criados com sucesso.')

create_test_data()
