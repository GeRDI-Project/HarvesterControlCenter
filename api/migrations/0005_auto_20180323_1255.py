# Generated by Django 2.0.3 on 2018-03-23 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20180323_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvester',
            name='repository',
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
    ]
