from django.db import migrations

def populate_module_flags(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    GroupModuleAccess = apps.get_model('core', 'GroupModuleAccess')

    perm_map = {
        'helpdesk': 'access_helpdesk',
        'approvals': 'access_approvals',
        'admin': 'access_admin',
    }

    # Build set of perm ids for quick lookup
    perm_ids = {key: None for key in perm_map}
    for key, code in perm_map.items():
        try:
            perm_ids[key] = Permission.objects.get(codename=code).id
        except Permission.DoesNotExist:
            perm_ids[key] = None

    for group in Group.objects.all():
        gma, _ = GroupModuleAccess.objects.get_or_create(group=group)
        perms = set(group.permissions.values_list('id', flat=True))
        gma.helpdesk = perm_ids['helpdesk'] in perms if perm_ids['helpdesk'] else gma.helpdesk
        gma.approvals = perm_ids['approvals'] in perms if perm_ids['approvals'] else gma.approvals
        gma.admin = perm_ids['admin'] in perms if perm_ids['admin'] else gma.admin
        gma.save()

def reverse_stub(apps, schema_editor):
    # No-op
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_groupmoduleaccess'),
    ]

    operations = [
        migrations.RunPython(populate_module_flags, reverse_stub),
    ]
