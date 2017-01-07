# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-07 14:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('konfera', '0026_auto_20161222_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='cfp_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Call for proposals deadline'),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='title',
            field=models.CharField(choices=[('none', ''), ('mr', 'Mr.'), ('ms', 'Ms.'), ('mx', 'Mx.')], default='none', max_length=4),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='title',
            field=models.CharField(choices=[('none', ''), ('mr', 'Mr.'), ('ms', 'Ms.'), ('mx', 'Mx.')], default='none', max_length=4),
        ),
    ]
