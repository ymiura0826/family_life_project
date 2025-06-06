# Generated by Django 5.2.1 on 2025-06-01 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_notifyschedule_notify_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationlog',
            name='group_id',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='notify_content',
            field=models.TextField(default='no set'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='response_code',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='notificationlog',
            name='response_message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
