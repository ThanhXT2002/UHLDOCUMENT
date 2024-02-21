# Generated by Django 5.0 on 2024-01-28 09:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_task_uploadfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='taskfiles',
            field=models.ManyToManyField(blank=True, related_name='task_uploadfiles', to='backend.uploadfiletask', verbose_name='file tiến độ'),
        ),
        migrations.AlterField(
            model_name='uploadfiletask',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upload_files', to='backend.task'),
        ),
    ]