# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-18 08:24
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('hash', models.CharField(max_length=64)),
                ('discount', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('available_from', models.DateTimeField()),
                ('available_to', models.DateTimeField()),
                ('usage', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='Event name')),
                ('slug', models.SlugField(help_text='Slug field, relative URL to the event.', verbose_name='Event url')),
                ('description', models.TextField()),
                ('date_from', models.DateTimeField(verbose_name='Event begging')),
                ('date_to', models.DateTimeField(verbose_name='Event end')),
                ('event_type', models.CharField(choices=[(b'conference', 'Conference'), (b'meetup', 'Meetup')], max_length=20)),
                ('status', models.CharField(choices=[(b'draft', 'Draft'), (b'published', 'Published'), (b'expired', 'Expired')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('street', models.CharField(max_length=128)),
                ('street2', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(max_length=128)),
                ('postcode', models.CharField(max_length=12)),
                ('state', models.CharField(max_length=128)),
                ('capacity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[(b'awaiting_payment', b'Awaiting payment'), (b'paid', b'Paid'), (b'expired', b'Expired'), (b'cancelled', b'Cancelled')], max_length=256)),
                ('purchase_date', models.DateTimeField()),
                ('payment_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('street', models.CharField(max_length=128)),
                ('street2', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(max_length=128)),
                ('postcode', models.CharField(max_length=12)),
                ('state', models.CharField(max_length=128)),
                ('companyid', models.CharField(blank=True, max_length=32, null=True)),
                ('taxid', models.CharField(blank=True, max_length=32, null=True)),
                ('vatid', models.CharField(blank=True, max_length=32, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('description', models.TextField()),
                ('duration', models.IntegerField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('title', models.CharField(choices=[(b'none', b''), (b'mr', b'Mr.'), (b'ms', b'Ms.')], default=b'none', max_length=4)),
                ('email', models.EmailField(max_length=255)),
                ('phone', models.CharField(max_length=64)),
                ('bio', models.TextField()),
                ('url', models.URLField(blank=True, null=True)),
                ('social_url', models.URLField(blank=True, null=True)),
                ('country', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('type', models.IntegerField(choices=[(1, b'Platinum'), (2, b'Gold'), (3, b'Silver'), (4, b'Bronze'), (5, b'Other'), (6, b'Django girls')])),
                ('logo', models.FileField(upload_to=b'')),
                ('url', models.URLField()),
                ('about_us', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('abstract', models.TextField()),
                ('type', models.CharField(choices=[(b'talk', b'Talk'), (b'workshop', b'Workshop')], max_length=32)),
                ('status', models.CharField(choices=[(b'cfp', b'Call For Proposals'), (b'draft', b'Draft'), (b'approved', b'Approved'), (b'rejected', b'Rejected'), (b'withdrawn', b'Withdrawn')], max_length=32)),
                ('duration', models.IntegerField(choices=[(5, b'5 min'), (30, b'30 min'), (45, b'45 min')])),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Event')),
                ('primary_speaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secondary_speaker', to='konfera.Speaker')),
                ('secondary_speaker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='primary_speaker', to='konfera.Speaker')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(b'requested', b'Requested'), (b'registered', b'Registered'), (b'checked-in', b'Checked-in'), (b'cancelled', b'Cancelled')], max_length=32)),
                ('title', models.CharField(choices=[(b'none', b''), (b'mr', b'Mr.'), (b'ms', b'Ms.')], default=b'none', max_length=4)),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
                ('description', models.TextField()),
                ('discount_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='konfera.DiscountCode')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Order')),
            ],
        ),
        migrations.CreateModel(
            name='TicketType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('attendee_type', models.CharField(choices=[(b'volunteer', 'Volunteer'), (b'press', 'Press'), (b'attendee', 'Attendee'), (b'supporter', 'Supporter'), (b'sponsor', 'Sponsor'), (b'aid', 'Aid')], default=b'attendee', max_length=255)),
                ('available_from', models.DateTimeField()),
                ('available_to', models.DateTimeField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Event')),
            ],
        ),
        migrations.AddField(
            model_name='ticket',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.TicketType'),
        ),
        migrations.AddField(
            model_name='speaker',
            name='sponsor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='konfera.Sponsor'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='talk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Talk'),
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Location'),
        ),
        migrations.AddField(
            model_name='event',
            name='sponsors',
            field=models.ManyToManyField(blank=True, related_name='sponsored_events', to='konfera.Sponsor'),
        ),
        migrations.AddField(
            model_name='discountcode',
            name='ticket_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.TicketType'),
        ),
    ]
