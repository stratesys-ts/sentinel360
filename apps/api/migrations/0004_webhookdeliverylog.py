from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_apirequestlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebhookDeliveryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=50)),
                ('target_url', models.URLField()),
                ('status_code', models.PositiveIntegerField(blank=True, null=True)),
                ('success', models.BooleanField(default=False)),
                ('error_message', models.CharField(blank=True, max_length=500)),
                ('response_body', models.TextField(blank=True)),
                ('attempt', models.PositiveIntegerField(default=1)),
                ('duration_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='api.webhooksubscription')),
            ],
            options={
                'verbose_name': 'Entrega de Webhook',
                'verbose_name_plural': 'Entregas de Webhook',
                'ordering': ['-created_at'],
            },
        ),
    ]
