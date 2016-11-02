# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-31 23:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('konfera', '0005_auto_20161024_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tickettype',
            name='accessibility',
            field=models.CharField(choices=[('public', 'Public'), ('private', 'Private'), ('disabled', 'Disabled'), ('not_listed', 'Not listed')], default='private', max_length=32),
        ),
    ]
