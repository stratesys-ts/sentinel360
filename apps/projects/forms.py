from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'status',
                  'external_access', 'cost_center', 'project_manager', 'currency',
                  'geography', 'industry', 'team']
        widgets = {
            # Use ISO format so HTML date inputs render the stored value
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'team': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'external_access': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'team': 'Membro de Equipe',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            input_type = getattr(field.widget, 'input_type', None)
            if input_type != 'checkbox' and not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs['class'] = 'form-control'
        
        # Filter team members to exclude clients
        from django.contrib.auth import get_user_model
        User = get_user_model()
        internal_users = User.objects.filter(is_active=True).exclude(role=User.Role.CLIENT).order_by('username')
        managers = internal_users.filter(role=User.Role.MANAGER)

        self.fields['team'].queryset = internal_users
        # Only managers in the manager dropdown
        self.fields['project_manager'].queryset = managers

        # Datas aceitam padrão ISO e pt-BR e exibem em ISO para o input date
        self.fields['start_date'].widget.format = '%Y-%m-%d'
        self.fields['end_date'].widget.format = '%Y-%m-%d'
        self.fields['start_date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']
        self.fields['end_date'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
