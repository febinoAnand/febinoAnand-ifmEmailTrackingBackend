# Generated by Django 4.2.4 on 2023-12-13 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0027_alter_rawdata_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawdata',
            name='datetime',
            field=models.DateTimeField(default='2023-12-13 12:20:10', editable=False),
        ),
    ]
