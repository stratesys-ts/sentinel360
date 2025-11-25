from django.db import migrations, models, transaction


def populate_ticket_public_id(apps, schema_editor):
    Ticket = apps.get_model('helpdesk', 'Ticket')
    with transaction.atomic():
        last = 0
        for ticket in Ticket.objects.order_by('id'):
            if ticket.public_id is None:
                last += 1
                ticket.public_id = last
                ticket.save(update_fields=['public_id'])


def unpopulate_ticket_public_id(apps, schema_editor):
    Ticket = apps.get_model('helpdesk', 'Ticket')
    Ticket.objects.update(public_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ('helpdesk', '0003_alter_category_options_alter_ticket_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='public_id',
            field=models.PositiveIntegerField(editable=False, null=True, unique=True),
        ),
        migrations.RunPython(populate_ticket_public_id, unpopulate_ticket_public_id),
    ]
