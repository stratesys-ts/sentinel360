from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_sync_reports_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupmoduleaccess',
            name='approvals_he',
            field=models.BooleanField(default=False),
        ),
    ]
