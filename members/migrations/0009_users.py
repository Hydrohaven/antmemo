# Generated by Django 5.0.6 on 2024-07-18 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_course_coreq_course_restriction'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('username', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
    ]
