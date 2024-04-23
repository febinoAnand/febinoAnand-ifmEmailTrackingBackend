# Generated by Django 4.2.4 on 2023-10-16 16:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0009_alter_token_options_remove_token_createdat_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='token',
            options={},
        ),
        migrations.RemoveField(
            model_name='token',
            name='created',
        ),
        migrations.RemoveField(
            model_name='token',
            name='key',
        ),
        migrations.AddField(
            model_name='token',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='id',
            field=models.BigAutoField(auto_created=True, default=123987263987, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='token',
            field=models.CharField(default=230958029385, max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='token',
            name='deviceID',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='devices.device'),
        ),
    ]
