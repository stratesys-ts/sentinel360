from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('timesheet', '0002_activity_alter_timeentry_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='partial_approvers',
            field=models.ManyToManyField(blank=True, related_name='partially_approved_timesheets', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='timesheet',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('SUBMITTED', 'Submitted'), ('PARTIALLY_APPROVED', 'Partially Approved'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='DRAFT', max_length=20),
        ),
    ]
