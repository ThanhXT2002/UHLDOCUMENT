# Generated by Django 5.0 on 2024-01-31 16:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_ethnicity_alter_account_ethnicity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Nationality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Quốc gia',
                'verbose_name_plural': 'Quốc gia',
            },
        ),
        migrations.AlterField(
            model_name='account',
            name='nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.nationality', verbose_name='Quốc tịch'),
        ),
    ]
