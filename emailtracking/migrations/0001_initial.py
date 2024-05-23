# Generated by Django 4.2.4 on 2024-05-23 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inbox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('from_email', models.EmailField(max_length=254)),
                ('to_email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('message_id', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(default='default_host', max_length=100)),
                ('port', models.IntegerField(default=8080)),
                ('username', models.CharField(default='default_username', max_length=100)),
                ('password', models.CharField(default='default_password', max_length=100)),
                ('checkstatus', models.BooleanField(default=False)),
                ('checkinterval', models.IntegerField(default=60)),
                ('phone', models.CharField(default='0000000000', max_length=15)),
                ('sid', models.CharField(default='default_sid', max_length=100)),
                ('auth_token', models.CharField(default='default_auth_token', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserEmailTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(max_length=25)),
                ('mobile', models.CharField(max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SearchParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('hunt_word', models.CharField(max_length=50, unique=True)),
                ('message', models.CharField(max_length=250)),
                ('user_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_user_group', to='auth.group')),
            ],
        ),
    ]
