# Generated by Django 4.2.4 on 2023-09-03 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_remove_eventgroup_events'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventgroup',
            name='events',
            field=models.ManyToManyField(related_name='eventGroup', to='events.event'),
        ),
    ]
