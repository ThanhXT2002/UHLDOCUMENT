# Generated by Django 5.0 on 2024-01-29 07:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_alter_uploadfiletask_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.BooleanField(choices=[(True, 'Xuất bản'), (False, 'Ngưng xuất bản')], default=True),
        ),
        migrations.CreateModel(
            name='CatagoryNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('tag', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Cập nhật gần nhất')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_cata_nofi', to=settings.AUTH_USER_MODEL, verbose_name='Người tạo')),
            ],
            options={
                'verbose_name_plural': 'Loại hông báo',
            },
        ),
        migrations.AddField(
            model_name='notification',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='notification_categories', to='backend.catagorynotification'),
        ),
    ]
