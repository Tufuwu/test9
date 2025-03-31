# Generated by Django 2.2.10 on 2020-02-13 09:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('a4_candy_organisations', '0006_social_media'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_info', jsonfield.fields.JSONField(blank=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.A4_ORGANISATIONS_MODEL)),
            ],
            options={
                'unique_together': {('member', 'organisation')},
            },
        ),
    ]
