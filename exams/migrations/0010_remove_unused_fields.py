# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-28 21:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0009_not_nullable_exam_run'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examauthorization',
            name='date_first_eligible',
        ),
        migrations.RemoveField(
            model_name='examauthorization',
            name='date_last_eligible',
        ),
    ]
