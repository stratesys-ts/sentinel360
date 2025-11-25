from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_groupmoduleaccess_approvals_he'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('access_helpdesk', 'Can access Helpdesk module'), ('access_approvals', 'Can access Approvals module'), ('access_approvals_he', 'Can access HE Approvals module'), ('access_admin', 'Can access Administration module'), ('access_reports', 'Can access Reports module')], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
