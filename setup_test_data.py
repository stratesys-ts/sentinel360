from apps.core.models import User
from apps.projects.models import Project
from apps.helpdesk.models import Ticket, Category
from django.contrib.auth.models import Group
from datetime import date

# 1. Create Project
project, created = Project.objects.get_or_create(
    name="Projeto Piloto Cliente",
    defaults={
        'description': "Projeto de teste para validação do portal.",
        'start_date': date.today(),
        'end_date': date.today(),
        'status': 'IN_PROGRESS'
    }
)
print(f"Projeto: {project}")

# 2. Create Client User
client_user, created = User.objects.get_or_create(
    username="cliente_teste",
    defaults={
        'email': "cliente@teste.com",
        'role': User.Role.CLIENT,
        'client_project': project
    }
)
if created:
    client_user.set_password("senha123")
    client_user.save()
    # Add to group
    group = Group.objects.get(name='Cliente externo')
    client_user.groups.add(group)
    print(f"Usuário criado: {client_user.username} / senha123")
else:
    print(f"Usuário já existe: {client_user.username}")

# 3. Create Ticket
category, _ = Category.objects.get_or_create(name="Suporte Geral", defaults={'sla_hours': 24})

Ticket.objects.create(
    title="Erro no acesso ao sistema",
    description="Não consigo acessar a tela de relatórios.",
    project=project,
    created_by=client_user,
    category=category,
    status='OPEN',
    priority='HIGH'
)
print("Ticket de teste criado.")
