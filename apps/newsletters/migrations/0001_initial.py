# Generated by Django 2.2.6 on 2019-10-24 13:08

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(settings.A4_ORGANISATIONS_MODEL),
        ('a4projects', '0024_group_on_delete_set_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(blank=True, editable=False, null=True)),
                ('sender_name', models.CharField(max_length=254, verbose_name='Name')),
                ('sender', models.EmailField(blank=True, max_length=254, verbose_name='Sender')),
                ('subject', models.CharField(max_length=254, verbose_name='Subject')),
                ('body', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Email body')),
                ('sent', models.DateTimeField(blank=True, null=True, verbose_name='Sent')),
                ('receivers', models.PositiveSmallIntegerField(choices=[(2, 'Users following a specific project'), (1, 'Users following your organisation'), (3, 'Every initiator of your organisation'), (0, 'Every user of the platform')], verbose_name='Receivers')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organisation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.A4_ORGANISATIONS_MODEL)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='a4projects.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
