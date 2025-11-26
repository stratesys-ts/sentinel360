from django import forms
from django.contrib.auth import get_user_model
from apps.projects.models import Project, Issue

User = get_user_model()


class TicketForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'priority', 'project', 'assigned_to', 'description', 'start_date', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def _project_members(self, project):
        members = list(project.team.all())
        if project.project_manager:
            members.append(project.project_manager)
        if project.project_owner:
            members.append(project.project_owner)
        return User.objects.filter(pk__in={m.pk for m in members})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Projeto obrigatorio e limitado aos projetos ativos
        self.fields['project'].required = True
        self.fields['project'].queryset = Project.objects.filter(status=Project.Status.IN_PROGRESS)

        # Responsavel limitado aos membros do projeto escolhido
        member_qs = User.objects.none()
        project_id = self.data.get('project') or getattr(self.instance, 'project_id', None)
        if project_id:
            try:
                project_obj = Project.objects.get(pk=project_id)
                member_qs = self._project_members(project_obj)
            except Project.DoesNotExist:
                pass
        self.fields['assigned_to'].queryset = member_qs
        self.fields['assigned_to'].required = False
        # Oculta o campo na criacao (apenas exibe em edicao)
        if self.instance.pk is None:
            self.fields['assigned_to'].widget = forms.HiddenInput()

        # Forca issue_type para Help Desk
        self.instance.issue_type = getattr(self.instance, 'issue_type', Issue.IssueType.HELP_DESK)

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_assigned_to(self):
        assigned = self.cleaned_data.get('assigned_to')
        project = self.cleaned_data.get('project')
        if assigned and project:
            allowed = self._project_members(project)
            if assigned not in allowed:
                raise forms.ValidationError("Responsavel precisa ser membro do projeto selecionado.")
        return assigned
