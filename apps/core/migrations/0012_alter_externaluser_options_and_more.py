from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_copy_approvals_to_he'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='externaluser',
            options={'verbose_name': 'Usuário externo', 'verbose_name_plural': 'Usuários externos'},
        ),
        migrations.AlterModelOptions(
            name='groupmoduleaccess',
            options={'verbose_name': 'Visibilidade de módulos do grupo', 'verbose_name_plural': 'Visibilidade de módulos do grupo'},
        ),
        migrations.AlterModelOptions(
            name='internaluser',
            options={'verbose_name': 'Usuário interno', 'verbose_name_plural': 'Usuários internos'},
        ),
    ]
