# Generated by Django 2.0.3 on 2018-03-23 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20180323_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='harvester',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
    ]