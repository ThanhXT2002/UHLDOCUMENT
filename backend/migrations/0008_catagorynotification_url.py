# Generated by Django 5.0 on 2024-01-29 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_alter_notification_status_catagorynotification_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='catagorynotification',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]