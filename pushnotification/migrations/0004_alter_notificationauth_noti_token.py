# Generated by Django 4.2.4 on 2024-05-07 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pushnotification', '0003_alter_setting_application_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationauth',
            name='noti_token',
            field=models.CharField(max_length=50),
        ),
    ]
