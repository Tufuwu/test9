# Generated by Django 2.0.13 on 2020-01-13 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odonto', '0037_auto_20200113_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orthodontictreatment',
            name='completion_type',
            field=models.CharField(blank=True, choices=[('Treatment completed', 'Treatment completed'), ('Treatment discontinued', 'Treatment discontinued'), ('Treatment abandoned - patient requested', 'Treatment abandoned - patient requested'), ('Treatment abandoned - patient failed to return', 'Treatment abandoned - patient failed to return')], max_length=256, null=True),
        ),
    ]
