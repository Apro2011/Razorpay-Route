# Generated by Django 5.0.1 on 2024-01-03 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0017_alter_recieversgroup_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='recieversgroup',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
