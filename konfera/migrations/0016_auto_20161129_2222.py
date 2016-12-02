# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-26 11:52
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    EmailTemplate = apps.get_model("konfera", "EmailTemplate")
    db_alias = schema_editor.connection.alias
    text = """Dear {first_name} {last_name},\n\n
order with your ticket for {event} has been updated.\n\n
Price: {price} {currency}\n
Amount paid: {amount_paid} {currency}\n
Processing fee: {processing_fee} {currency}\n
Discount: {discount} {currency}\n
Status: {status}\n
Purchase date: {purchase_date}\n
Payment date: {payment_date}\n\n\n

{event} organizers team."""
    html = """Dear {first_name} {last_name},<br /><br />
order with your ticket for {event} has been updated.<br /><br />
Price: {price} {currency}<br />
Amount paid: {amount_paid} {currency}<br />
Processing fee: {processing_fee} {currency}<br />
Discount: {discount} {currency}<br />
Status: {status}<br />
Purchase date: {purchase_date}<br />
Payment date: {payment_date}<br /><br /><br />
{event} organizers team."""
    EmailTemplate.objects.using(db_alias).bulk_create([
        EmailTemplate(name="order_update_email", counter=0, text_template=text, html_template=html),
    ])


def reverse_func(apps, schema_editor):
    EmailTemplate = apps.get_model("konfera", "EmailTemplate")
    db_alias = schema_editor.connection.alias
    EmailTemplate.objects.using(db_alias).filter(name="order_update_email").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('konfera', '0015_auto_20161127_2133'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]
