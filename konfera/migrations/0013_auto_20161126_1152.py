# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 11:52
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    EmailTemplate = apps.get_model("konfera", "EmailTemplate")
    db_alias = schema_editor.connection.alias
    text = """Dear {first_name} {last_name},\n\n
              thank you for purchasing ticket for {event}.\n
              Your order details are available at url: {order_url}\n\n\n
              Looking forward to see you.\n\n
              PyCon SK team.\n\n
              {event_url}\n"""
    html = """Dear {first_name} {last_name},<br /><br />
              thank you for purchasing ticket for <strong><a href=\"{event_url}\">{event}</a></strong>.<br />
              Your order details are available at url: <a href=\"{order_url}\">{order_url}</a><br /><br /><br />
              Looking forward to see you.<br /><br />
              PyCon SK team.<br />"""
    EmailTemplate.objects.using(db_alias).bulk_create([
        EmailTemplate(name="register_email", counter=0, text_template=text, html_template=html),
    ])


def reverse_func(apps, schema_editor):
    EmailTemplate = apps.get_model("konfera", "EmailTemplate")
    db_alias = schema_editor.connection.alias
    EmailTemplate.objects.using(db_alias).filter(name="register_email").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('konfera', '0012_auto_20161126_1151'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
