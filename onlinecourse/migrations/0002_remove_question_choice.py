# Generated by Django 3.1.3 on 2023-08-08 00:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='choice',
        ),
    ]
