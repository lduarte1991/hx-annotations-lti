# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hx_lti_initializer', '0007_auto_20150727_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lticourse',
            name='course_external_css_default',
            field=models.CharField(help_text=b'Please only input a URL to an externally hosted CSS file.', max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
