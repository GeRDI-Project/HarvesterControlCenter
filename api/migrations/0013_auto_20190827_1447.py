# Generated by Django 2.2 on 2019-08-27 12:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20181212_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvester',
            name='name',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z_]+$', 'Only alphanumeric characters and underscore are allowed.')]),
        ),
    ]
