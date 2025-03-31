# Generated by Django 2.2.10 on 2020-03-13 09:23

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("caluma_workflow", "0020_case_families")]

    operations = [
        migrations.AddField(
            model_name="historicaltask",
            name="control_groups",
            field=models.TextField(
                blank=True,
                help_text="Group jexl returning what group(s) derived work items will be assigned to for controlling.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="historicalworkitem",
            name="controlling_groups",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=150),
                default=list,
                help_text="List of groups this work item is assigned to for controlling.",
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="control_groups",
            field=models.TextField(
                blank=True,
                help_text="Group jexl returning what group(s) derived work items will be assigned to for controlling.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="workitem",
            name="controlling_groups",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=150),
                default=list,
                help_text="List of groups this work item is assigned to for controlling.",
                size=None,
            ),
        ),
    ]
