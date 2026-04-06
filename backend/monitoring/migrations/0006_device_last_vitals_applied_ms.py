from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("monitoring", "0005_remove_patient_news2_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="device",
            name="last_vitals_applied_ms",
            field=models.BigIntegerField(
                null=True,
                blank=True,
                help_text="HL7/REST dan bemorga oxirgi muvaffaqiyatli vital yozilgan vaqt (ms).",
            ),
        ),
    ]
