from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = apps.get_model('core', 'User')

    defaults = {
        'email': 'admin@erp.com',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
    }

    admin, created = User.objects.get_or_create(username='admin', defaults=defaults)

    if created:
        admin.password = make_password('admin')
        admin.save()
        return

    updated = False
    for attr, value in defaults.items():
        if getattr(admin, attr) != value:
            setattr(admin, attr, value)
            updated = True

    if updated:
        admin.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_user_force_password_change'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, migrations.RunPython.noop),
    ]
