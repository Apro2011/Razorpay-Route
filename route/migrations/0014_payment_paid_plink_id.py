# Generated by Django 5.0 on 2023-12-26 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0013_payment_paid_amount_payment_paid_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='paid_plink_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]