# Generated by Django 4.2.18 on 2025-02-18 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bot', '0015_delete_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(verbose_name='Дата конца')),
                ('report_data', models.JSONField(verbose_name='Содержимое')),
                ('is_sent', models.BooleanField(default=False, verbose_name='Отправлен')),
                ('confirmed_by', models.ManyToManyField(blank=True, to='bot.userstate', verbose_name='Подтвержден')),
            ],
            options={
                'verbose_name': 'Отчет',
                'verbose_name_plural': 'Отчеты',
            },
        ),
    ]
