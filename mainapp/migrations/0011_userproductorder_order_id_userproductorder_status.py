# Generated by Django 4.2.15 on 2024-09-29 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_alter_customuser_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproductorder',
            name='order_id',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='userproductorder',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('ordered', 'ordered'), ('Delivered', 'Delivered')], default='pending', max_length=10),
        ),
    ]