# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-06-19 06:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lan', '0017_lan_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lan',
            options={'ordering': ['start_date'], 'permissions': (('export_paying_participants', 'Can export list of paying participants to downloadable file'), ('register_arrivals', 'Can show and register arrivals'), ('register_new_user', 'Can directly register a new user')), 'verbose_name': 'LAN', 'verbose_name_plural': 'LANs'},
        ),
    ]
