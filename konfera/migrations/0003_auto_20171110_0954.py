# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-10 09:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('konfera', '0002_talk_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('private', 'Private')], max_length=20),
        ),
        migrations.AlterField(
            model_name='talk',
            name='duration',
            field=models.IntegerField(choices=[(30, '30 min'), (45, '45 min'), (60, '60 min'), (90, '90 min'), (120, '120 min'), (180, '180 min'), (240, '240 min')], default=30, help_text='Talk duration in minutes.'),
        ),
    ]
