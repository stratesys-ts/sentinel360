from django.conf import settings
from django.db import migrations, models


def copy_colleague_to_colleagues(apps, schema_editor):
    Issue = apps.get_model('projects', 'Issue')
    db_alias = schema_editor.connection.alias

    for issue in Issue.objects.using(db_alias).all():
        colleague_id = getattr(issue, 'colleague_id', None)
        if colleague_id:
            issue.colleagues.add(colleague_id)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_issue_colleague_alter_issue_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='colleagues',
            field=models.ManyToManyField(
                blank=True,
                related_name='colleague_issues',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Colega de Trabalho',
            ),
        ),
        migrations.RunPython(copy_colleague_to_colleagues, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='issue',
            name='colleague',
        ),
    ]
