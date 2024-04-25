# Generated by Django 4.2.4 on 2024-04-25 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EmailTracking', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('hunt_word', models.CharField(max_length=50, unique=True)),
                ('message', models.CharField(max_length=250)),
                ('mobile', models.CharField(max_length=10)),
                ('country_code', models.CharField(max_length=3)),
            ],
        ),
        migrations.AddField(
            model_name='inbox',
            name='message_id',
            field=models.IntegerField(null=True),
        ),
    ]