# Generated by Django 4.2.4 on 2023-12-13 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0023_alter_button_buttonmode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='button',
            name='buttonMode',
            field=models.CharField(choices=[('AUTO', 'auto'), ('MANUAL', 'manual'), ('AUTO+MANUAL', 'auto+manual')], default='auto', max_length=15),
        ),
    ]
