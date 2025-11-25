from django.db import migrations

def sync_reports(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    GroupModuleAccess = apps.get_model('core', 'GroupModuleAccess')
    try:
        perm = Permission.objects.get(codename='access_reports')
    except Permission.DoesNotExist:
        perm = None

    for g in Group.objects.all():
        gma, _ = GroupModuleAccess.objects.get_or_create(group=g)
        if g.name == 'Administrador' or g.name == 'Recursos Humanos':
            gma.reports = True
        gma.save()
        # sync permission if available
        if perm:
            if gma.reports:
                g.permissions.add(perm)
            else:
                g.permissions.remove(perm)

def reverse_stub(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_alter_user_options_groupmoduleaccess_reports'),
    ]

    operations = [
        migrations.RunPython(sync_reports, reverse_stub),
    ]
