# Generated by Django 5.0.1 on 2024-01-04 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0019_payment_created_by_reciever_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reciever',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]