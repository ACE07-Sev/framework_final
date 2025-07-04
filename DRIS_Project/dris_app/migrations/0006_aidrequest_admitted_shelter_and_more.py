# Generated by Django 5.2.3 on 2025-06-23 18:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dris_app", "0005_volunteerassignment_citizen_confirmed"),
    ]

    operations = [
        migrations.AddField(
            model_name="aidrequest",
            name="admitted_shelter",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dris_app.shelter",
            ),
        ),
        migrations.AlterField(
            model_name="aidrequest",
            name="aid_type",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="aidrequest",
            name="details",
            field=models.TextField(blank=True),
        ),
    ]
