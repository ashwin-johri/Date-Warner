# Generated by Django 4.2.10 on 2024-04-11 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myASD', '0004_submission_reporter_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='dating_platform',
            field=models.CharField(choices=[('bumble', 'Bumble'), ('hinge', 'Hinge'), ('tinder', 'Tinder'), ('other', 'Other')], max_length=50),
        ),
    ]
