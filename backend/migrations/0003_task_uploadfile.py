# Generated by Django 5.0 on 2024-01-28 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_remove_task_uploadfiles_task_taskfiles'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='uploadfile',
            field=models.ManyToManyField(blank=True, related_name='admin_uploadfiles', to='backend.uploadfile', verbose_name='file đính kèm'),
        ),
    ]
