# Generated by Django 4.2.4 on 2024-05-07 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pushnotification', '0002_setting_application_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='application_id',
            field=models.CharField(max_length=50),
        ),
    ]
