# Generated by Django 4.0.2 on 2022-02-14 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_auto_20220214_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
