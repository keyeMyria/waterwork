# Generated by Django 2.0 on 2018-10-22 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dmam', '0005_auto_20181022_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='dmaid',
            field=models.ManyToManyField(to='dmam.DMABaseinfo'),
        ),
    ]