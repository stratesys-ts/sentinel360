from django.db import migrations, models, transaction


def populate_task_public_id(apps, schema_editor):
    Task = apps.get_model('projects', 'Task')
    with transaction.atomic():
        last = 0
        for task in Task.objects.order_by('id'):
            if task.public_id is None:
                last += 1
                task.public_id = last
                task.save(update_fields=['public_id'])


def unpopulate_task_public_id(apps, schema_editor):
    Task = apps.get_model('projects', 'Task')
    Task.objects.update(public_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_merge_20251124_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='public_id',
            field=models.PositiveIntegerField(editable=False, null=True, unique=True),
        ),
        migrations.RunPython(populate_task_public_id, unpopulate_task_public_id),
    ]
