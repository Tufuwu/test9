# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-05 12:15
from __future__ import unicode_literals

import uuid

from django.db import migrations


def create_address_books(apps, schema_editor):
    """Create address books for every account."""
    User = apps.get_model("core", "User")
    AddressBook = apps.get_model("modoboa_contacts", "AddressBook")
    for user in User.objects.filter(mailbox__isnull=False):
        abook = AddressBook.objects.create(
            name="Contacts", user=user, _path="contacts")
        for contact in user.contact_set.all():
            contact.addressbook = abook
            contact.uid = "{}.vcf".format(uuid.uuid4())
            contact.save()


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('modoboa_contacts', '0003_auto_20181005_1415'),
    ]

    operations = [
        migrations.RunPython(create_address_books, backward)
    ]
