# Generated by Django 4.2.4 on 2023-12-03 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0020_alter_rawdata_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawdata',
            name='datetime',
            field=models.DateTimeField(default='2023-12-03 10:34:16', editable=False),
        ),
    ]