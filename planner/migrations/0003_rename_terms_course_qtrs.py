# Generated by Django 4.1.3 on 2022-11-14 01:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0002_alter_course_terms_alter_schedule_end_year_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="course",
            old_name="terms",
            new_name="qtrs",
        ),
    ]