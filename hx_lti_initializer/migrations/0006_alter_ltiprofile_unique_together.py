# Generated by Django 3.2.18 on 2023-03-14 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hx_lti_initializer', '0005_alter_lticourse_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ltiprofile',
            unique_together={('anon_id', 'scope')},
        ),
    ]
