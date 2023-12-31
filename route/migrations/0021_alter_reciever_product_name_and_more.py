# Generated by Django 5.0.1 on 2024-01-04 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0020_reciever_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reciever',
            name='product_name',
            field=models.CharField(default='route', max_length=100),
        ),
        migrations.AlterField(
            model_name='reciever',
            name='tnc_accepted',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='reciever',
            name='type',
            field=models.CharField(default='route', max_length=20),
        ),
    ]
