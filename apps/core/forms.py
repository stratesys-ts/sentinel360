from django.contrib.auth.admin import UserChangeForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .models import InternalUser, ExternalUser

class InternalUserForm(forms.ModelForm):
    class Meta:
        model = InternalUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'client_project']

class ExternalUserForm(forms.ModelForm):
    class Meta:
        model = ExternalUser
        fields = ['username', 'email', 'first_name', 'last_name', 'client_project']

class InternalUserPasswordForm(UserChangeForm):
    new_password = forms.CharField(
        label=_("Senha"),
        widget=forms.PasswordInput(render_value=True),
        required=False,
    )
    confirm_password = forms.CharField(
        label=_("Confirmação"),
        widget=forms.PasswordInput(render_value=True),
        required=False,
    )
    generate_password = forms.BooleanField(
        label=_("Gerar uma senha"),
        required=False,
        initial=False,
    )
    force_password_change = forms.BooleanField(
        label=_("Tem que alterar a senha no próximo login"),
        required=False,
        initial=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        info = (
            '<div class="password-note">Deve ter, pelo menos, 8 caracteres.</div>'
            '<div class="password-note">Deve conter letras maiúsculas, minúsculas, dígitos e caracteres especiais.</div>'
        )
        self.fields['new_password'].help_text = mark_safe(info)
        if self.instance and self.instance.pk:
            self.fields['force_password_change'].initial = self.instance.force_password_change
        else:
            self.fields['force_password_change'].initial = False

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('new_password')
        confirm = cleaned.get('confirm_password')
        if not pwd and not confirm:
            return cleaned
        if not pwd:
            self.add_error('new_password', _("Digite uma senha."))
        if pwd and not confirm:
            self.add_error('confirm_password', _("Confirme a senha."))
        if pwd and confirm and pwd != confirm:
            self.add_error('confirm_password', _("As senhas não conferem."))
        return cleaned
