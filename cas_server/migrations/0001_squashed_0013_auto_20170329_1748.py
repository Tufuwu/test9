# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-04-29 17:40
from __future__ import unicode_literals

import cas_server.utils
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('cas_server', '0001_squashed_0021_auto_20150611_2102'), ('cas_server', '0002_auto_20151212_1300'), ('cas_server', '0003_auto_20151212_1721'), ('cas_server', '0004_auto_20151218_1032'), ('cas_server', '0005_auto_20160616_1018'), ('cas_server', '0006_auto_20160706_1727'), ('cas_server', '0007_auto_20160723_2252'), ('cas_server', '0008_newversionwarning'), ('cas_server', '0009_auto_20160814_0619'), ('cas_server', '0010_auto_20160824_2112'), ('cas_server', '0011_auto_20161007_1258'), ('cas_server', '0012_auto_20170328_1610'), ('cas_server', '0013_auto_20170329_1748')]

    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proxy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='ProxyGrantingTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributs', models.TextField(blank=True, default=None, null=True)),
                ('validate', models.BooleanField(default=False)),
                ('service', models.TextField()),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('renew', models.BooleanField(default=False)),
                ('value', models.CharField(default=cas_server.utils.gen_pgt, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProxyTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributs', models.TextField(blank=True, default=None, null=True)),
                ('validate', models.BooleanField(default=False)),
                ('service', models.TextField()),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('renew', models.BooleanField(default=False)),
                ('value', models.CharField(default=cas_server.utils.gen_pt, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServicePattern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pos', models.IntegerField(default=100)),
                ('pattern', models.CharField(max_length=255, unique=True)),
                ('user_field', models.CharField(blank=True, default=b'', help_text=b"Nom de l'attribut transmit comme username, vide = login", max_length=255)),
                ('usernames', models.CharField(blank=True, default=b'', help_text=b"Liste d'utilisateurs accept\xc3\xa9s s\xc3\xa9par\xc3\xa9 par des virgules, vide = tous les utilisateur", max_length=255)),
                ('attributs', models.CharField(blank=True, default=b'', help_text=b"Liste des nom d'attributs \xc3\xa0 transmettre au service, s\xc3\xa9par\xc3\xa9 par une virgule. vide = aucun", max_length=255)),
                ('proxy', models.BooleanField(default=False, help_text=b"Un ProxyGrantingTicket peut \xc3\xaatre d\xc3\xa9livr\xc3\xa9 au service pour s'authentifier en temps que l'utilisateur sur d'autres services")),
                ('filter', models.CharField(blank=True, default=b'', help_text=b'Une lambda fonction pour filtrer sur les utilisateur o\xc3\xb9 leurs attribut, arg1: username, arg2:attrs_dict. vide = pas de filtre', max_length=255)),
            ],
            options={
                'ordering': ('pos',),
            },
        ),
        migrations.CreateModel(
            name='ServiceTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributs', models.TextField(blank=True, default=None, null=True)),
                ('validate', models.BooleanField(default=False)),
                ('service', models.TextField()),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('renew', models.BooleanField(default=False)),
                ('value', models.CharField(default=cas_server.utils.gen_st, max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('date', models.DateTimeField(auto_now=True)),
                ('session_key', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='serviceticket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='serviceticket', to='cas_server.User'),
        ),
        migrations.AddField(
            model_name='proxyticket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proxyticket', to='cas_server.User'),
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proxygrantingticket', to='cas_server.User'),
        ),
        migrations.AddField(
            model_name='proxy',
            name='proxy_ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proxies', to='cas_server.ProxyTicket'),
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='service_pattern',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='proxygrantingticket', to='cas_server.ServicePattern'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proxyticket',
            name='service_pattern',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='proxyticket', to='cas_server.ServicePattern'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='serviceticket',
            name='service_pattern',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='serviceticket', to='cas_server.ServicePattern'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ReplaceAttributName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="nom d'un attributs \xe0 transmettre au service", max_length=255)),
                ('replace', models.CharField(blank=True, help_text="nom sous lequel l'attribut sera pr\xe9sent\xe9 au service. vide = inchang\xe9", max_length=255)),
                ('service_pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributs', to='cas_server.ServicePattern')),
            ],
        ),
        migrations.RemoveField(
            model_name='servicepattern',
            name='attributs',
        ),
        migrations.CreateModel(
            name='FilterAttributValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribut', models.CharField(help_text='Name of the attribute which must verify pattern', max_length=255, verbose_name='attribute')),
                ('pattern', models.CharField(help_text='a regular expression', max_length=255, validators=[cas_server.utils.regexpr_validator], verbose_name='pattern')),
                ('service_pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filters', to='cas_server.ServicePattern')),
            ],
        ),
        migrations.CreateModel(
            name='ReplaceAttributValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribut', models.CharField(help_text='Name of the attribute for which the value must be replace', max_length=255, verbose_name='attribute')),
                ('pattern', models.CharField(help_text='An regular expression maching whats need to be replaced', max_length=255, validators=[cas_server.utils.regexpr_validator], verbose_name='pattern')),
                ('replace', models.CharField(blank=True, help_text='replace expression, groups are capture by \\1, \\2 \u2026', max_length=255, verbose_name='replace')),
                ('service_pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replacements', to='cas_server.ServicePattern')),
            ],
        ),
        migrations.RemoveField(
            model_name='servicepattern',
            name='filter',
        ),
        migrations.CreateModel(
            name='Username',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(help_text='username allowed to connect to the service', max_length=255, verbose_name='username')),
                ('service_pattern', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usernames', to='cas_server.ServicePattern')),
            ],
        ),
        migrations.RemoveField(
            model_name='servicepattern',
            name='usernames',
        ),
        migrations.AddField(
            model_name='servicepattern',
            name='restrict_users',
            field=models.BooleanField(default=False, help_text='Limit username allowed to connect to the list provided bellow', verbose_name='restrict username'),
        ),
        migrations.AddField(
            model_name='servicepattern',
            name='name',
            field=models.CharField(blank=True, help_text='A name for the service', max_length=255, null=True, unique=True, verbose_name='name'),
        ),
        migrations.AlterUniqueTogether(
            name='replaceattributname',
            unique_together=set([('name', 'replace', 'service_pattern')]),
        ),
        migrations.AddField(
            model_name='servicepattern',
            name='single_log_out',
            field=models.BooleanField(default=False, help_text='Enable SLO for the service', verbose_name='single log out'),
        ),
        migrations.AlterField(
            model_name='replaceattributname',
            name='name',
            field=models.CharField(help_text='name of an attribut to send to the service', max_length=255, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='replaceattributname',
            name='replace',
            field=models.CharField(blank=True, help_text='name under which the attribut will be showto the service. empty = default name of the attribut', max_length=255, verbose_name='replace'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='pattern',
            field=models.CharField(max_length=255, unique=True, verbose_name='pattern'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='pos',
            field=models.IntegerField(default=100, verbose_name='position'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='proxy',
            field=models.BooleanField(default=False, help_text='A ProxyGrantingTicket can be delivered to the service in order to authenticate for the user on a backend service', verbose_name='proxy'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='user_field',
            field=models.CharField(blank=True, default=b'', help_text='Name of the attribut to transmit as username, empty = login', max_length=255, verbose_name='user field'),
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='single_log_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='proxyticket',
            name='single_log_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='serviceticket',
            name='single_log_out',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='servicepattern',
            name='proxy_callback',
            field=models.BooleanField(default=False, help_text='can be used as a proxy callback to deliver PGT', verbose_name='proxy callback'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='proxy',
            field=models.BooleanField(default=False, help_text='Proxy tickets can be delivered to the service', verbose_name='proxy'),
        ),
        migrations.AddField(
            model_name='servicepattern',
            name='single_log_out_callback',
            field=models.CharField(blank=True, default=b'', help_text='URL where the SLO request will be POST. empty = service url\nThis is usefull for non HTTP proxied services.', max_length=255, verbose_name='single log out callback'),
        ),
        migrations.AlterField(
            model_name='replaceattributname',
            name='name',
            field=models.CharField(help_text='name of an attribut to send to the service, use * for all attributes', max_length=255, verbose_name='name'),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('username', 'session_key')]),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='pattern',
            field=models.CharField(help_text="A regular expression matching services. Will usually looks like '^https://some\\.server\\.com/path/.*$'.As it is a regular expression, special character must be escaped with a '\\'.", max_length=255, unique=True, verbose_name='pattern'),
        ),
        migrations.AlterModelOptions(
            name='servicepattern',
            options={'ordering': ('pos',), 'verbose_name': 'Service pattern', 'verbose_name_plural': 'Services patterns'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='pos',
            field=models.IntegerField(default=100, help_text='service patterns are sorted using the position attribute', verbose_name='position'),
        ),
        migrations.CreateModel(
            name='FederatedIendityProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suffix', models.CharField(help_text='Suffix append to backend CAS returner username: `returned_username`@`suffix`', max_length=30, unique=True, verbose_name='suffix')),
                ('server_url', models.CharField(max_length=255, verbose_name='server url')),
                ('cas_protocol_version', models.CharField(choices=[(b'1', b'CAS 1.0'), (b'2', b'CAS 2.0'), (b'3', b'CAS 3.0'), (b'CAS_2_SAML_1_0', b'SAML 1.1')], default=b'3', help_text='Version of the CAS protocol to use when sending requests the the backend CAS', max_length=30, verbose_name='CAS protocol version')),
                ('verbose_name', models.CharField(help_text='Name for this identity provider displayed on the login page', max_length=255, verbose_name='verbose name')),
                ('pos', models.IntegerField(default=100, help_text='Identity provider are sorted using the (position, verbose name, suffix) attributes', verbose_name='position')),
                ('display', models.BooleanField(default=True, help_text='Display the provider on the login page', verbose_name='display')),
            ],
            options={
                'verbose_name': 'identity provider',
                'verbose_name_plural': 'identity providers',
            },
        ),
        migrations.CreateModel(
            name='FederatedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=124)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cas_server.FederatedIendityProvider')),
                ('ticket', models.CharField(max_length=255)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('_attributs', models.TextField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='federateduser',
            unique_together=set([('username', 'provider')]),
        ),
        migrations.CreateModel(
            name='FederateSLO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('ticket', models.CharField(db_index=True, max_length=255)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='federateslo',
            unique_together=set([('username', 'session_key', 'ticket')]),
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='cas_protocol_version',
            field=models.CharField(choices=[(b'1', b'CAS 1.0'), (b'2', b'CAS 2.0'), (b'3', b'CAS 3.0'), (b'CAS_2_SAML_1_0', b'SAML 1.1')], default=b'3', help_text='Version of the CAS protocol to use when sending requests the the backend CAS.', max_length=30, verbose_name='CAS protocol version'),
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='display',
            field=models.BooleanField(default=True, help_text='Display the provider on the login page.', verbose_name='display'),
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='pos',
            field=models.IntegerField(default=100, help_text='Position of the identity provider on the login page. Identity provider are sorted using the (position, verbose name, suffix) attributes.', verbose_name='position'),
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='suffix',
            field=models.CharField(help_text='Suffix append to backend CAS returner username: ``returned_username`` @ ``suffix``.', max_length=30, unique=True, verbose_name='suffix'),
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='verbose_name',
            field=models.CharField(help_text='Name for this identity provider displayed on the login page.', max_length=255, verbose_name='verbose name'),
        ),
        migrations.RemoveField(
            model_name='proxygrantingticket',
            name='attributs',
        ),
        migrations.RemoveField(
            model_name='proxyticket',
            name='attributs',
        ),
        migrations.RemoveField(
            model_name='serviceticket',
            name='attributs',
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='_attributs',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='proxyticket',
            name='_attributs',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='serviceticket',
            name='_attributs',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='suffix',
            field=models.CharField(help_text='Suffix append to backend CAS returned username: ``returned_username`` @ ``suffix``.', max_length=30, unique=True, verbose_name='suffix'),
        ),
        migrations.CreateModel(
            name='NewVersionWarning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='replaceattributname',
            name='name',
            field=models.CharField(help_text='name of an attribute to send to the service, use * for all attributes', max_length=255, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='replaceattributname',
            name='replace',
            field=models.CharField(blank=True, help_text='name under which the attribute will be showto the service. empty = default name of the attribut', max_length=255, verbose_name='replace'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='user_field',
            field=models.CharField(blank=True, default=b'', help_text='Name of the attribute to transmit as username, empty = login', max_length=255, verbose_name='user field'),
        ),
        migrations.AlterField(
            model_name='replaceattributname',
            name='replace',
            field=models.CharField(blank=True, help_text='name under which the attribute will be show to the service. empty = default name of the attribut', max_length=255, verbose_name='replace'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='pattern',
            field=models.CharField(help_text="A regular expression matching services. Will usually looks like '^https://some\\.server\\.com/path/.*$'.As it is a regular expression, special character must be escaped with a '\\'.", max_length=255, unique=True, validators=[cas_server.utils.regexpr_validator], verbose_name='pattern'),
        ),
        migrations.CreateModel(
            name='UserAttributes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_attributs', models.TextField(blank=True, default=None, null=True)),
                ('username', models.CharField(max_length=155, unique=True)),
            ],
            options={
                'verbose_name': 'User attributes cache',
                'verbose_name_plural': 'User attributes caches',
            },
        ),
        migrations.AlterModelOptions(
            name='federateduser',
            options={'verbose_name': 'Federated user', 'verbose_name_plural': 'Federated users'},
        ),
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='federatediendityprovider',
            name='cas_protocol_version',
            field=models.CharField(choices=[('1', 'CAS 1.0'), ('2', 'CAS 2.0'), ('3', 'CAS 3.0'), ('CAS_2_SAML_1_0', 'SAML 1.1')], default='3', help_text='Version of the CAS protocol to use when sending requests the the backend CAS.', max_length=30, verbose_name='CAS protocol version'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='single_log_out_callback',
            field=models.CharField(blank=True, default='', help_text='URL where the SLO request will be POST. empty = service url\nThis is usefull for non HTTP proxied services.', max_length=255, verbose_name='single log out callback'),
        ),
        migrations.AlterField(
            model_name='servicepattern',
            name='user_field',
            field=models.CharField(blank=True, default='', help_text='Name of the attribute to transmit as username, empty = login', max_length=255, verbose_name='user field'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=250),
        ),
    ]
