# Generated by Django 4.2.4 on 2023-10-29 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0015_device_devicepassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='device',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='devices.device'),
        ),
    ]
