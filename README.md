# Sentinel360 (ERP Django)

Sistema ERP com mÃ³dulos de Help Desk, Timesheet e Projetos.

## Recursos
- AutenticaÃ§Ã£o com funÃ§Ãµes: Admin, Manager, Collaborator, Client.
- Help Desk: chamados com SLA, categorias e comentÃ¡rios.
- Timesheet: apontamento de horas com fluxo de aprovaÃ§Ã£o.
- Projetos: Kanban, tarefas e visÃ£o de cronograma simples.
- Dashboard: indicadores e atividade recente.

## Stack
- Backend: Python 3.11+, Django 5.0+, DRF (drf-yasg para Swagger/Redoc).
- DB: PostgreSQL (prod/Docker) e SQLite (dev opcional); ORM Django.
- Front: Django Templates, Bootstrap 5, CSS custom, FontAwesome 6, JS vanilla.
- Infra: Docker/Docker Compose, WhiteNoise, python-dotenv.

## InstalaÃ§Ã£o RÃ¡pida
1. Clonar: `git clone https://github.com/stratesys-ts/sentinel360.git && cd sentinel360`
2. Virtualenv: `python -m venv .venv && .venv\Scripts\activate`
3. DependÃªncias: `pip install -r requirements.txt`
4. DB (Docker): `docker-compose up -d`
5. Migra??es: `python manage.py migrate` (a migra??o agora garante o superuser `admin/admin`, evitando falhas de login ap?s trocar de branch)
6. Dados demo: `python create_fixtures.py`
7. Rodar: `python manage.py runserver`
8. Acesso: http://127.0.0.1:8000 (admin/admin, manager/manager, collab/collab, client/client)

## Estrutura
- apps/core: autenticaÃ§Ã£o e dashboard
- apps/helpdesk: chamados
- apps/timesheet: horas e aprovaÃ§Ãµes
- apps/projects: projetos, tarefas e kanban

## Onboarding RÃ¡pido (Git)
1. Clonar e ativar venv (passos acima).
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py runserver`
5. Fluxo Git:
   - Atualizar: `git pull origin main`
   - Trabalhar em branch: `git checkout -b feature/minha-tarefa`
   - Commit/push: `git add . && git commit -m "mensagem" && git push -u origin feature/minha-tarefa`
   - PR e merge; depois `git checkout main && git pull`
6. Se precisar resetar para o remoto: `git fetch origin && git checkout main && git reset --hard origin/main`

## VS Code + GitHub (Fluxo RÃ¡pido)
1. ExtensÃµes: GitHub Pull Requests, GitLens, Python.
2. Clone via VS Code (`Ctrl+Shift+P` > Git: Clone) com URL GitHub.
3. Terminal integrado: `.venv\Scripts\activate`.
4. Branch: `git checkout -b feature/minha-tarefa`.
5. Commit: `git add .` e `git commit -m "mensagem"`.
6. Push: `git push -u origin feature/minha-tarefa`.
7. Abrir PR (Source Control ou browser). ApÃ³s merge: `git checkout main && git pull`.

## VS Code + Git + Azure DevOps
1. ExtensÃµes: Azure Repos (ou GitHub se usar integraÃ§Ã£o), GitLens, Python.
2. Clone via VS Code (`Ctrl+Shift+P` > Git: Clone) com URL do Azure Repos.
3. Ativar venv e instalar deps se preciso.
4. Branch: `git checkout -b feature/minha-tarefa`.
5. Commit: `git add . && git commit -m "mensagem"`.
6. Push: `git push -u origin feature/minha-tarefa` (use token do Azure se pedir).
7. Abrir PR no Azure DevOps (Repos > Pull Requests) e selecionar revisores.
8. Depois do merge: `git checkout main && git pull`.

## Problemas Comuns
- ModuleNotFoundError: `pip install -r requirements.txt`
- Erro no runserver: ative venv e rode `python manage.py migrate`
