# Generated by Django 3.0.4 on 2020-09-23 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_customizationrequest'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customizationrequest',
            old_name='number_of_students',
            new_name='num_students',
        ),
        migrations.RenameField(
            model_name='customizationrequest',
            old_name='why',
            new_name='reason',
        ),
    ]
