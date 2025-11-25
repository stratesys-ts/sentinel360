from django.db import migrations


def copy_flags(apps, schema_editor):
    GroupModuleAccess = apps.get_model('core', 'GroupModuleAccess')
    GroupModuleAccess.objects.filter(approvals=True).update(approvals_he=True)


def reverse_copy(apps, schema_editor):
    GroupModuleAccess = apps.get_model('core', 'GroupModuleAccess')
    GroupModuleAccess.objects.update(approvals_he=False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_user_options'),
    ]

    operations = [
        migrations.RunPython(copy_flags, reverse_copy),
    ]
