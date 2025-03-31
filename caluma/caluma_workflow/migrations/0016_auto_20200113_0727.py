# Generated by Django 2.2.8 on 2020-01-13 07:27

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("caluma_workflow", "0015_add_work_item_skipped")]

    operations = [
        migrations.RemoveIndex(model_name="case", name="workflow_ca_meta_08775a_gin"),
        migrations.RemoveIndex(model_name="task", name="workflow_ta_meta_6864a4_gin"),
        migrations.RemoveIndex(
            model_name="workflow", name="workflow_wo_meta_2ac517_gin"
        ),
        migrations.RemoveIndex(
            model_name="workitem", name="workflow_wo_address_679262_gin"
        ),
        migrations.RemoveIndex(
            model_name="workitem", name="workflow_wo_assigne_76d859_gin"
        ),
        migrations.RemoveIndex(
            model_name="workitem", name="workflow_wo_meta_2704a2_gin"
        ),
        migrations.AddIndex(
            model_name="case",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["meta"], name="caluma_work_meta_5cd3f3_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["meta"], name="caluma_work_meta_25e8ed_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="workflow",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["meta"], name="caluma_work_meta_42c1ce_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["addressed_groups"], name="caluma_work_address_23d0a8_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["assigned_users"], name="caluma_work_assigne_7880f0_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="workitem",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["meta"], name="caluma_work_meta_f6fc45_gin"
            ),
        ),
    ]
