from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organization", "0002_jobposition_required_skill_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="agency",
            name="seeded_on",
            field=models.DateField(blank=True, null=True),
        ),
    ]
