# Generated by Django 2.1.7 on 2019-04-16 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hx_lti_initializer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TargetObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_title', models.CharField(max_length=255)),
                ('target_author', models.CharField(max_length=255)),
                ('target_content', models.TextField()),
                ('target_citation', models.TextField(blank=True)),
                ('target_created', models.DateTimeField(auto_now_add=True)),
                ('target_updated', models.DateTimeField(auto_now=True)),
                ('target_type', models.CharField(choices=[('tx', 'Text Annotation'), ('vd', 'Video Annotation'), ('ig', 'Image Annotation')], default='tx', max_length=2)),
                ('target_courses', models.ManyToManyField(to='hx_lti_initializer.LTICourse')),
                ('target_creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='hx_lti_initializer.LTIProfile')),
            ],
            options={
                'ordering': ['target_title'],
                'verbose_name': 'Source',
            },
        ),
    ]
