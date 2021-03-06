# Generated by Django 2.0 on 2018-10-22 15:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dmam', '0004_vcommunity_commutid'),
    ]

    operations = [
        migrations.CreateModel(
            name='DmaStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_id', models.CharField(max_length=30)),
                ('meter_type', models.CharField(max_length=30)),
                ('station_type', models.CharField(max_length=30)),
                ('dmaid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dmam.DMABaseinfo')),
            ],
            options={
                'db_table': 'dmastation',
                'managed': True,
            },
        ),
        migrations.RemoveField(
            model_name='dmastations',
            name='dmaid',
        ),
        migrations.AlterField(
            model_name='station',
            name='dmaid',
            field=models.ManyToManyField(null=True, to='dmam.DMABaseinfo'),
        ),
        migrations.DeleteModel(
            name='DmaStations',
        ),
    ]
