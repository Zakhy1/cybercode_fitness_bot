# Generated by Django 4.2.18 on 2025-02-16 08:24

import bot.models.cheque
import bot.models.circle
import bot.models.contract
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0012_userstate_banned'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cheque',
            options={'verbose_name': 'Чек', 'verbose_name_plural': 'Чеки'},
        ),
        migrations.AlterModelOptions(
            name='circle',
            options={'verbose_name': 'Кружок', 'verbose_name_plural': 'Кружки'},
        ),
        migrations.AlterModelOptions(
            name='contract',
            options={'verbose_name': 'Договор', 'verbose_name_plural': 'Договоры'},
        ),
        migrations.AlterModelOptions(
            name='report',
            options={'verbose_name': 'Отчет', 'verbose_name_plural': 'Отчеты'},
        ),
        migrations.AlterModelOptions(
            name='userstate',
            options={'verbose_name': 'Состояние пользователя', 'verbose_name_plural': 'Состояния пользователей'},
        ),
        migrations.RemoveField(
            model_name='userstate',
            name='has_contract',
        ),
        migrations.AlterField(
            model_name='cheque',
            name='file',
            field=models.FileField(upload_to=bot.models.cheque.user_directory_path, verbose_name='Файл чека'),
        ),
        migrations.AlterField(
            model_name='cheque',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Загружен'),
        ),
        migrations.AlterField(
            model_name='cheque',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.userstate', verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='circle',
            name='file',
            field=models.FileField(upload_to=bot.models.circle.user_directory_path, verbose_name='Видео'),
        ),
        migrations.AlterField(
            model_name='circle',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Загружен'),
        ),
        migrations.AlterField(
            model_name='circle',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.userstate', verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='file',
            field=models.FileField(upload_to=bot.models.contract.user_directory_path, verbose_name='Файл договора'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='uploaded_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Загружен'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.userstate', verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='report',
            name='confirmed_by',
            field=models.ManyToManyField(blank=True, to='bot.userstate', verbose_name='Подтвержден'),
        ),
        migrations.AlterField(
            model_name='report',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Создан'),
        ),
        migrations.AlterField(
            model_name='report',
            name='end_date',
            field=models.DateField(verbose_name='Дата конца'),
        ),
        migrations.AlterField(
            model_name='report',
            name='is_sent',
            field=models.BooleanField(default=False, verbose_name='Отправлен'),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_data',
            field=models.JSONField(verbose_name='Содержимое'),
        ),
        migrations.AlterField(
            model_name='report',
            name='start_date',
            field=models.DateField(verbose_name='Дата начала'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='banned',
            field=models.BooleanField(default=False, verbose_name='Заблокирован'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='chat_id',
            field=models.BigIntegerField(unique=True, verbose_name='ID чата'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='confirmation_code',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='Код подтверждения'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Адрес электронной почты'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='is_registered',
            field=models.BooleanField(default=False, verbose_name='Зарегистрирован'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='ФИО'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='send_reports',
            field=models.BooleanField(default=False, verbose_name='Отправлять отчеты'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='state',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Состояние'),
        ),
        migrations.AlterField(
            model_name='userstate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
    ]
