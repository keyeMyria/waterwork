# Generated by Django 2.0.5 on 2018-07-05 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PorgressBar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totoal', models.IntegerField(default=1)),
                ('progress', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterModelOptions(
            name='organizations',
            options={'managed': True, 'permissions': (('firmmanager', '企业管理'), ('rolemanager_firmmanager', '角色管理'), ('rolemanager_firmmanager_edit', '角色管理_可写'), ('organusermanager_firmmanager', '组织和用户管理'), ('organusermanager_firmmanager_edit', '组织和用户管理_可写'))},
        ),
    ]