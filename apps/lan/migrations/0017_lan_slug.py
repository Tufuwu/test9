# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-16 17:26
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lan', '0016_auto_20200216_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='lan',
            name='slug',
            field=models.SlugField(blank=True, help_text='Optional. Must be alphanumeric and start with a letter.', validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z][a-zA-Z0-9]*$')], verbose_name='slug'),
        ),
    ]
