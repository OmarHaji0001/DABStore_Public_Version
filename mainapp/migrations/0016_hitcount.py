# Generated by Django 4.2.15 on 2024-10-08 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_orders_delivered_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hitcount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('count', models.IntegerField(default=0)),
            ],
        ),
    ]
