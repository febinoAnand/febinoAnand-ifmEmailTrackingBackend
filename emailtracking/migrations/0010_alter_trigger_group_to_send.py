# Generated by Django 4.2.4 on 2024-05-08 18:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('emailtracking', '0009_alter_trigger_group_to_send'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trigger',
            name='group_to_send',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trigger_group', to='auth.group'),
        ),
    ]