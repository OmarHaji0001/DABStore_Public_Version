# Generated by Django 4.2.15 on 2024-09-21 20:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theme',
            name='about2',
        ),
    ]
