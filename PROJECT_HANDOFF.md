# ERP / Portal (Stratesys) — Handoff Rápido

## Objetivo do app
Portal único para gestão de projetos, tarefas/timesheets, help desk e administração de usuários (internos/externos) com navegação moderna (Unfold no admin) e visão separada por perfil (admin/consultor/cliente).

## Estado atual (principais features)
- **Autenticação e perfis**: login/logout, papéis (Admin, Manager/Consultor, Cliente) e permissões básicas por grupos; menu lateral condicionado a permissões.
- **Admin (Unfold)**: cadastros de usuários internos/externos, grupos e visibilidade de módulos; tela de confirmação de exclusão customizada; menu “Users” oculto; bulk delete ajustado; labels PT-BR.
- **Projetos**:
  - CRUD com campos: nome, descrição, datas, status, orçamento, moeda, centro de custo, geografia, indústria, acesso externo, gerente, equipe (sem campo Dono), custo/centro de custo.
  - Listagem: colunas Nome, Status, Início, Fim, Acesso Externo, Progresso, Total Horas, Ações.
  - Detalhe: tabs para Geral, Tarefas, Kanban, Riscos, Horas trabalhadas; resumo em grid responsivo; botões Editar/Excluir alinhados no cabeçalho.
  - Páginas dedicadas: `/projects/<id>/tasks`, `/kanban`, `/risks` (conteúdo básico; Kanban estático sem drag-and-drop; Riscos placeholder).
- **Tarefas**: modelo com título, descrição, responsável, status, prioridade, prazo; tabela nas rotas de tarefas; Kanban por status.
- **Timesheets**: lançamento/aprovação de horas, atividades gerenciáveis no admin; card “Horas no mês” soma horas do usuário logado.
- **Help Desk**: tickets com categorias/prioridades/status; menu chamador no dashboard.
- **UI/UX**:
  - Dashboard cards clicáveis (Help Desk, Timesheet, Projetos; Tarefas sem link).
  - Dropdown de usuário com páginas de Perfil/Configurações (placeholders funcionais).
  - Botão “Abrir Novo Chamado” sem sublinhado.
  - Admin delete confirmation mais elegante; botões de exclusão ajustados.

## Avanços de hoje
- Removido campo Dono (form e resumo); datas do projeto aceitam `YYYY-MM-DD` e `DD/MM/YYYY`.
- Detalhe do projeto redesenhado em grid, com tabs apontando para páginas dedicadas.
- Lista de projetos: removido Cliente; adicionado Acesso Externo; rótulos corrigidos.
- Páginas novas por tab: tarefas/kanban/riscos dedicadas, com tab ativo pelo contexto.
- Botões Editar/Excluir alinhados ao título no detalhe do projeto.

## Próximos passos sugeridos
- **Tarefas/Kanban**: adicionar filtros/ações (criar/editar), e drag-and-drop no Kanban.
- **Riscos**: criar modelo/listagem (título, impacto, probabilidade, responsável, status, mitigação) e exibir na página de riscos.
- **Perfil/Configurações**: implementar conteúdo real (dados editáveis, troca de senha, preferências/idioma/notificações).
- **Notificações**: alertas para tarefas atrasadas/atribuídas.
- **Relatórios**: horas por tarefa/usuário/projeto; progresso real em projetos.
- **API**: endpoints de projetos/tarefas/time entries para BI/automações.
- **UI**: adicionar acentuação onde ainda houver encoding quebrado (ex.: “Orçamento”, “Indústria”, “Descrição” já tratados em algumas telas, revisar admin e demais templates).
