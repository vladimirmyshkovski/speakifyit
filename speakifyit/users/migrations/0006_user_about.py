# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-11-21 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_middle_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='about',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
