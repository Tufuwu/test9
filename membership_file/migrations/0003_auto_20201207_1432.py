# Generated by Django 2.2.17 on 2020-12-07 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership_file', '0002_auto_20200914_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='country',
            field=models.CharField(default='NL', max_length=255),
        ),
    ]
