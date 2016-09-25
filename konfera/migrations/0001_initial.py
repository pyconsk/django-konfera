# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 10:55
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
                ('date_from', models.DateTimeField(verbose_name='Beginning')),
                ('date_to', models.DateTimeField(verbose_name='End')),
                ('title', models.CharField(max_length=128, verbose_name='Event name')),
                ('slug', models.SlugField(help_text='Slug field, relative URL to the event.', verbose_name='Event url')),
                ('description', models.TextField()),
                ('event_type', models.CharField(choices=[('conference', 'Conference'), ('meetup', 'Meetup')], max_length=20)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('expired', 'Expired')], max_length=20)),
            ],
            options={
                'abstract': False,
            },
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
                ('status', models.CharField(choices=[('awaiting_payment', 'Awaiting payment'), ('paid', 'Paid'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='awaiting_payment', max_length=20)),
                ('purchase_date', models.DateTimeField(auto_now_add=True)),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
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
                ('description', models.TextField(blank=True, help_text='Description will be displayed, only if there is no related talk, eg. coffee break, lunch etc...')),
                ('duration', models.IntegerField(default=0, help_text='Duration in minutes.', validators=[django.core.validators.MaxValueValidator(300), django.core.validators.MinValueValidator(0)])),
                ('room', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_rooms', to='konfera.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('title', models.CharField(choices=[('none', ''), ('mr', 'Mr.'), ('ms', 'Ms.')], default='none', max_length=4)),
                ('email', models.EmailField(max_length=255)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
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
                ('type', models.IntegerField(choices=[(1, 'Platinum'), (2, 'Gold'), (3, 'Silver'), (4, 'Bronze'), (5, 'Other'), (6, 'Django girls')])),
                ('logo', models.FileField(upload_to='')),
                ('url', models.URLField()),
                ('about_us', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('abstract', models.TextField(help_text='Abstract will be published in the schedule.')),
                ('abstract', models.TextField(help_text='Abstract will be published in the schedule.')),
                ('type', models.CharField(choices=[('talk', 'Talk'), ('workshop', 'Workshop')], default='talk', max_length=32)),
                ('status', models.CharField(choices=[('cfp', 'Call For Proposals'), ('draft', 'Draft'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn')], max_length=32)),
                ('duration', models.IntegerField(choices=[(5, '5 min'), (30, '30 min'), (45, '45 min')], default=30, help_text='Talk duration in minutes.')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Event')),
                ('primary_speaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary_speaker_talks', to='konfera.Speaker', verbose_name='Primary speaker')),
                ('secondary_speaker', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='secondary_speaker_talks', to='konfera.Speaker', verbose_name='Secondary speaker')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('requested', 'Requested'), ('registered', 'Registered'), ('checked-in', 'Checked-in'), ('cancelled', 'Cancelled')], max_length=32)),
                ('title', models.CharField(choices=[('none', ''), ('mr', 'Mr.'), ('ms', 'Ms.')], default='none', max_length=4)),
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
                ('date_from', models.DateTimeField(verbose_name='Beginning')),
                ('date_to', models.DateTimeField(verbose_name='End')),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('attendee_type', models.CharField(choices=[('volunteer', 'Volunteer'), ('press', 'Press'), ('attendee', 'Attendee'), ('supporter', 'Supporter'), ('sponsor', 'Sponsor'), ('aid', 'Aid')], default='attendee', max_length=255)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.Event')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='ticket',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='konfera.TicketType'),
        ),
        migrations.AddField(
            model_name='speaker',
            name='sponsor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sponsored_speakers', to='konfera.Sponsor'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='talk',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_talks', to='konfera.Talk'),
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
