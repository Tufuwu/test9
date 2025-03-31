# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-26 16:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bgjobs', '0005_auto_20190128_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backgroundjob',
            name='project',
            field=models.ForeignKey(help_text='Project in which this objects belongs', null=True, on_delete=django.db.models.deletion.CASCADE, to='projectroles.Project'),
        ),
    ]
