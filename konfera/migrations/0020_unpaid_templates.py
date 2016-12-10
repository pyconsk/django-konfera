# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    EmailTemplate = apps.get_model("konfera", "EmailTemplate")
    db_alias = schema_editor.connection.alias
    text = """Dear {first_name} {last_name},\n\n
order with your ticket for {event} hasn't been paid yet.\n\n
Please pay for it as soon as possible otherwise your ticket will expire.\n\n\n

{event} organizers team."""
    html = """Dear {first_name} {last_name},<br /><br />
order with your ticket for {event} hasn't been paid yet.<br /><br />
Please pay for it as soon as possible otherwise your ticket will expire.<br /><br /><br />

{event} organizers team."""
    EmailTemplate.objects.using(db_alias).bulk_create([
        EmailTemplate(name="unpaid_order_notification", counter=0, text_template=text, html_template=html),
    ])


def reverse_func(apps, schema_editor):
    EmailTemplate = apps.get_model("konfera", "EmailTemplate")
    db_alias = schema_editor.connection.alias
    EmailTemplate.objects.using(db_alias).filter(name="order_update_email").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('konfera', '0019_talk_language'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
