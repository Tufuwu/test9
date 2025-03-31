# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-24 12:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(help_text='Show Announcement')),
                ('title', models.TextField(help_text='Title (Text)')),
                ('content', models.TextField(help_text='Content (HTML)')),
            ],
        ),
    ]
