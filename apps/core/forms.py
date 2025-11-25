from django import forms
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from apps.projects.models import Project

User = get_user_model()

class ExternalUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=30, required=True, label="Sobrenome")
    email = forms.EmailField(required=True, label="E-mail")
    client_project = forms.ModelChoiceField(
        queryset=Project.objects.filter(external_access=True),
        required=True,
        label="Projeto",
        help_text="Selecione o projeto ao qual este usuário terá acesso."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'client_project']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.role = User.Role.CLIENT
        
        # Generate random password
        password = get_random_string(length=12)
        user.set_password(password)
        
        if commit:
            user.save()
            
        # Store the raw password on the user instance so it can be displayed once
        user._generated_password = password
        return user

class InternalUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nome")
    last_name = forms.CharField(max_length=30, required=True, label="Sobrenome")
    email = forms.EmailField(required=True, label="E-mail")
    role = forms.ChoiceField(
        choices=[
            (User.Role.ADMIN, 'Admin'),
            (User.Role.MANAGER, 'Manager'),
            (User.Role.COLLABORATOR, 'Collaborator'),
        ],
        required=True,
        label="Função"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        
        # Generate random password
        password = get_random_string(length=12)
        user.set_password(password)
        
        if commit:
            user.save()
            
        user._generated_password = password
        return user
