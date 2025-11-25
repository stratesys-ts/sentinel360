# Guia Rápido de Comandos e Consultas Django

Este documento reúne os comandos e consultas mais utilizados no dia a dia para gerenciar o App ERP.

## 1. Terminal (PowerShell)

Comandos para executar no terminal do VS Code ou PowerShell.

| Ação | Comando |
|------|---------|
| **Rodar o servidor** | `python manage.py runserver` |
| **Abrir o Shell Interativo** | `python manage.py shell` |
| **Criar Migrações** | `python manage.py makemigrations` |
| **Aplicar Migrações** | `python manage.py migrate` |
| **Criar Superusuário** | `python manage.py createsuperuser` |
| **Coletar Arquivos Estáticos** | `python manage.py collectstatic` |

---

## 2. Django Shell (Consultas ao Banco)

Para executar estes comandos, primeiro entre no shell com `python manage.py shell`.

### Importações Necessárias

Sempre comece importando seus modelos:

```python
from apps.core.models import User
from apps.projects.models import Project, Task
from apps.timesheet.models import TimeEntry
from apps.helpdesk.models import Ticket
```

### Consultas Básicas (Leitura)

**Listar todos os registros:**

```python
User.objects.all()
Project.objects.all()
```

**Buscar um registro específico (por ID ou campo único):**

```python
# Pelo ID
projeto = Project.objects.get(id=1)

# Pelo Username
usuario = User.objects.get(username='admin')
```

**Filtrar registros (retorna uma lista):**

```python
# Projetos em andamento
em_andamento = Project.objects.filter(status='IN_PROGRESS')

# Tarefas de alta prioridade
urgentes = Task.objects.filter(priority='HIGH')
```

### Consultas Avançadas

**Busca por texto (Case-insensitive):**

```python
# Projetos que contêm "web" no nome
projetos_web = Project.objects.filter(name__icontains='web')
```

**Busca por data:**

```python
from datetime import date
# Projetos que começaram depois de 01/01/2024
novos = Project.objects.filter(start_date__gt=date(2024, 1, 1))
```

**Acessar Relacionamentos:**

```python
projeto = Project.objects.get(id=1)

# Todas as tarefas deste projeto
tarefas = projeto.tasks.all()

# Cliente do projeto
cliente = projeto.client
```

### Criar e Atualizar Dados

**Criar um novo registro:**

```python
# Exemplo criando um Projeto
novo_projeto = Project.objects.create(
    name="Novo Sistema",
    description="Descrição do sistema",
    start_date="2024-02-01",
    end_date="2024-05-01",
    status="PLANNED"
)
```

**Atualizar um registro:**

```python
projeto = Project.objects.get(id=1)
projeto.status = 'COMPLETED'
projeto.save()  # Não esqueça do .save()!
```

**Deletar um registro:**

```python
# CUIDADO: Isso apaga do banco de dados
Task.objects.get(id=5).delete()
```
