import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organization", "0002_jobposition_required_skill_and_more"),
        ("workforce", "0002_certification_hrnote_leaverequest_payprofile_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Applicant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("skill", models.CharField(blank=True, max_length=80)),
                ("status", models.CharField(default="applied", max_length=16)),
                ("note", models.CharField(blank=True, max_length=240)),
                ("is_demo", models.BooleanField(default=False)),
                ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="applicants", to="organization.department")),
                ("hired_employee", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="application", to="workforce.employee")),
                ("position", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="applicants", to="organization.jobposition")),
                ("site", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="applicants", to="organization.clientsite")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
