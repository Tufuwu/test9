# Generated by Django 2.2.10 on 2020-03-05 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0038_remove_partnertypemapping_salesforce_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='lead_sharing',
            field=models.BooleanField(default=False),
        ),
    ]
