# Generated by Django 5.2 on 2025-05-15 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_remove_customuser_bio_remove_customuser_username_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="images/profile/"),
        ),
    ]
