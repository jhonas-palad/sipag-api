# Generated by Django 5.0.7 on 2024-09-20 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waste', '0010_remove_cleanerpoints_id_alter_cleanerpoints_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='redeemrecord',
            name='claimed_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='claimed date'),
        ),
    ]
