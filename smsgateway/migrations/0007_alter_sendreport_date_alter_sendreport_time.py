# Generated by Django 4.2.4 on 2024-05-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smsgateway', '0006_alter_sendreport_date_alter_sendreport_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendreport',
            name='date',
            field=models.DateField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='sendreport',
            name='time',
            field=models.TimeField(editable=False, null=True),
        ),
    ]
