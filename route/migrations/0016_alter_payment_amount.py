# Generated by Django 5.0 on 2023-12-26 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0015_alter_payment_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.IntegerField(),
        ),
    ]
