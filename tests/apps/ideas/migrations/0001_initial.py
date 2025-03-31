# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-10 09:58
from __future__ import unicode_literals

import adhocracy4.categories.fields
import adhocracy4.maps.fields
import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('a4categories', '0001_initial'),
        ('a4modules', '0004_description_maxlength_512'),
    ]

    operations = [
        migrations.CreateModel(
            name='Idea',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='a4modules.Item')),
                ('name', models.CharField(default='Can i haz cheezburger, pls?', max_length=120)),
                ('description', ckeditor.fields.RichTextField(blank=True, verbose_name='Description')),
                ('point', adhocracy4.maps.fields.PointField(blank=True)),
                ('point_label', models.CharField(blank=True, default='', help_text='This could be an address or the name of a landmark.', max_length=255, verbose_name='Label of the ideas location')),
                ('category', adhocracy4.categories.fields.CategoryField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='a4categories.Category', verbose_name='Category')),
            ],
            options={
                'abstract': False,
            },
            bases=('a4modules.item',),
        ),
    ]
