# Generated by Django 4.2.18 on 2025-02-04 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_rename_first_name_userstate_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstate',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
