# Generated by Django 4.2.4 on 2023-12-13 12:17

from django.db import migrations, models
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_alter_eventgroup_machines'),
    ]

    operations = [
        migrations.AddField(
            model_name='button',
            name='buttonDO',
            field=models.IntegerField(default=0, validators=[events.models.unique_default]),
        ),
        migrations.AddField(
            model_name='button',
            name='buttonMode',
            field=models.CharField(choices=[('AUTO', 'auto'), ('MANUAL', 'manual')], default='AUTO', max_length=10),
        ),
    ]
