# Generated by Django 5.0.7 on 2024-08-31 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('waste', '0002_alter_wastereportactivity_activity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wastereportactivity',
            options={'ordering': ['-activity_timestamp']},
        ),
    ]
