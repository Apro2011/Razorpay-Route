# Generated by Django 5.0.1 on 2024-01-06 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0030_payment_group_name_payment_paid_at_reciever_paid_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recieversgroup',
            name='amount_paid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
