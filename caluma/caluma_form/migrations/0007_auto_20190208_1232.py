# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-08 12:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("caluma_form", "0006_choice_type_conversion")]

    operations = [
        migrations.AlterModelOptions(
            name="answerdocument", options={"ordering": ["-sort"]}
        ),
        migrations.AlterModelOptions(
            name="formquestion", options={"ordering": ["-sort"]}
        ),
        migrations.AlterModelOptions(
            name="questionoption", options={"ordering": ["-sort"]}
        ),
    ]
