# Generated by Django 3.0.4 on 2020-10-05 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('salesforce', '0058_partnerreview'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partnerreview',
            old_name='star_rating',
            new_name='rating',
        ),
    ]
