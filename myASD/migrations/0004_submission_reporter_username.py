# Generated by Django 4.2.10 on 2024-03-20 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myASD', '0003_submission_admin_notes_submission_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='reporter_username',
            field=models.CharField(default='none', editable=False, max_length=255),
            preserve_default=False,
        ),
    ]
