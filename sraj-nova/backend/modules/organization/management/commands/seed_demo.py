from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from decimal import Decimal

from common.crypto import encrypt
from modules.finance.models import CashMovement
from modules.finance.services import rebuild_week_invoices
from modules.identity.models import AgencyRole, User
from modules.operations.models import AttendanceEvent, OperationalAlert, ShiftAssignment, StaffingRequest
from modules.organization.models import Agency, Client, ClientSite, Department, JobPosition, ServiceContract
from modules.workforce.models import (
    Certification,
    Deployment,
    Employee,
    EmployeeIdentifier,
    EmploymentContract,
    HrNote,
    LeaveRequest,
    LegalEmployerKind,
    PayProfile,
    Qualification,
    RecruitmentEvent,
)

DEMO = "Synthetic demonstration record. Not a real company, worker, or Ghana identification number."
PASSWORD = "Demo-Only-Change-Me-1"


class Command(BaseCommand):
    help = "Load labelled synthetic agency data. Refuses to run when DEBUG is false."

    def handle(self, *args, **options):
        if not settings.DEBUG and not settings.FORCE_SEED_DEMO:
            raise CommandError("Refusing to seed demonstration data while DEBUG is false.")
        with transaction.atomic():
            self._load()
        self.stdout.write(self.style.WARNING(DEMO))
        self.stdout.write(f"Demonstration password: {PASSWORD}")

    def _load(self):
        Agency.objects.update_or_create(
            legal_name="SRAJ NOVA Ltd",
            defaults={
                "trading_name": "SRAJ NOVA",
                "country": "GH",
                "currency": "GHS",
                "timezone": "Africa/Accra",
            },
        )
        ashanti = self._client("sample-ashanti-textile", "Sample Ashanti Textile Works", "Manufacturing")
        tema = self._client("sample-tema-logistics", "Sample Tema Logistics Park", "Logistics")
        weaving = self._site(ashanti, "Sample Weaving Hall", "Kumasi", "Ashanti", "Weaving")
        yard = self._site(tema, "Sample Dispatch Yard", "Tema", "Greater Accra", "Dispatch")
        weaver = JobPosition.objects.get_or_create(client=ashanti, title="Weaving operator")[0]
        loader = JobPosition.objects.get_or_create(client=tema, title="Dispatch loader")[0]
        weaver.required_skill = "weaving"
        loader.required_skill = "dispatch"
        weaver.save(update_fields=["required_skill", "updated_at"])
        loader.save(update_fields=["required_skill", "updated_at"])
        today = timezone.localdate()
        people = [
            ("SN-1001", "Ama", "Mensah", ashanti, weaving, weaver, LegalEmployerKind.AGENCY, None, time(6, 0), "on_time"),
            ("SN-1002", "Kofi", "Boateng", ashanti, weaving, weaver, LegalEmployerKind.CLIENT, ashanti, time(6, 0), "late"),
            ("SN-1003", "Esi", "Owusu", ashanti, weaving, weaver, LegalEmployerKind.AGENCY, None, time(6, 0), "absent"),
            ("SN-2001", "Yaw", "Darko", tema, yard, loader, LegalEmployerKind.AGENCY, None, time(7, 0), "on_time"),
        ]
        for number, first, last, client, site, position, employer, employer_client, start, attendance in people:
            employee = Employee.objects.update_or_create(
                agency_employee_number=number,
                defaults={"first_name": first, "last_name": last, "status": "active", "is_demo": True},
            )[0]
            EmployeeIdentifier.objects.get_or_create(
                employee=employee,
                kind="ghana_card",
                defaults={"ciphertext": encrypt(f"SAMPLE-NOT-A-REAL-ID-{number}"), "is_synthetic": True},
            )
            EmploymentContract.objects.update_or_create(
                employee=employee,
                is_current=True,
                defaults={
                    "legal_employer_kind": employer,
                    "legal_employer_client": employer_client,
                    "starts_on": today - timedelta(days=40),
                    "ends_on": None,
                },
            )
            Deployment.objects.update_or_create(
                employee=employee,
                is_current=True,
                defaults={
                    "client": client,
                    "site": site["site"],
                    "department": site["department"],
                    "position": position,
                    "starts_on": today - timedelta(days=30),
                },
            )
            shift = ShiftAssignment.objects.update_or_create(
                employee=employee,
                work_date=today,
                defaults={
                    "client": client,
                    "site": site["site"],
                    "department": site["department"],
                    "position": position,
                    "starts_at": start,
                    "ends_at": time(14, 0),
                },
            )[0]
            self._punch(employee, today, start, attendance, shift)
            self._skill(employee, "weaving" if position == weaver else "dispatch", Decimal("20.00") if position == weaver else Decimal("18.00"))
        self._available_weaver(ashanti, weaving, weaver, today)
        ShiftAssignment.objects.get_or_create(
            client=ashanti,
            site=weaving["site"],
            department=weaving["department"],
            position=weaver,
            employee=None,
            work_date=today,
            defaults={"starts_at": time(14, 0), "ends_at": time(22, 0)},
        )
        ServiceContract.objects.update_or_create(
            client=ashanti,
            title="Sample weaving labour agreement",
            defaults={
                "billing_model": "cost_plus",
                "management_fee_rate": Decimal("0.1200"),
                "starts_on": today - timedelta(days=200),
                "ends_on": today + timedelta(days=20),
                "is_demo": True,
            },
        )
        ServiceContract.objects.update_or_create(
            client=tema,
            title="Sample dispatch labour agreement",
            defaults={
                "billing_model": "cost_plus",
                "management_fee_rate": Decimal("0.1000"),
                "starts_on": today - timedelta(days=100),
                "ends_on": today + timedelta(days=200),
                "is_demo": True,
            },
        )
        StaffingRequest.objects.get_or_create(
            client=ashanti,
            site=weaving["site"],
            title="Sample request for two night weavers",
            defaults={"headcount": 2, "status": "pending", "is_demo": True},
        )
        OperationalAlert.objects.get_or_create(
            message="Sample night shift at the weaving hall has no assigned operator.",
            defaults={"client": ashanti, "severity": "warning", "is_open": True},
        )
        owner = self._user("nova.owner@sample.sraj.test", "Nana", "Sarpong", AgencyRole.AGENCY_OWNER)
        self._user("nova.ops@sample.sraj.test", "Akua", "Frimpong", AgencyRole.AGENCY_OPERATIONS)
        self._user("client.ashanti@sample.sraj.test", "Kojo", "Asare", AgencyRole.CLIENT_USER, client=ashanti)
        worker = Employee.objects.get(agency_employee_number="SN-1001")
        self._user("worker.ama@sample.sraj.test", "Ama", "Mensah", AgencyRole.EMPLOYEE, employee=worker)
        owner.is_demo = True
        owner.save(update_fields=["is_demo"])
        ama = Employee.objects.get(agency_employee_number="SN-1001")
        Certification.objects.get_or_create(employee=ama, name="Sample loom safety certificate", defaults={"expires_on": today + timedelta(days=200)})
        LeaveRequest.objects.get_or_create(employee=ama, starts_on=today + timedelta(days=14), ends_on=today + timedelta(days=16), defaults={"status": "approved"})
        RecruitmentEvent.objects.get_or_create(
            employee=ama,
            summary="Sample application accepted for a weaving operator role.",
            defaults={"occurred_on": today - timedelta(days=45)},
        )
        HrNote.objects.get_or_create(
            employee=ama,
            visibility="standard",
            defaults={"body": "Sample orientation completed at the weaving hall."},
        )
        HrNote.objects.get_or_create(
            employee=ama,
            visibility="restricted",
            defaults={"body": "Sample restricted HR note. Hidden from the client portal."},
        )
        rebuild_week_invoices(today)
        CashMovement.objects.update_or_create(
            description="Sample opening cash balance",
            defaults={"occurred_on": today, "amount": Decimal("2500.00"), "is_demo": True},
        )

    def _client(self, slug, name, sector):
        return Client.objects.update_or_create(
            slug=slug,
            defaults={"legal_name": name, "sector": sector, "status": "active", "is_demo": True, "demo_label": DEMO},
        )[0]

    def _site(self, client, name, city, region, department):
        site = ClientSite.objects.get_or_create(
            client=client, name=name, defaults={"city": city, "region": region, "is_demo": True}
        )[0]
        department_row = Department.objects.get_or_create(site=site, name=department)[0]
        return {"site": site, "department": department_row}

    def _punch(self, employee, today, start, attendance, shift):
        AttendanceEvent.objects.filter(employee=employee, occurred_at__date=today).delete()
        if attendance == "absent":
            return
        minute = start.hour * 60 + start.minute - 5
        if attendance == "late":
            minute = start.hour * 60 + start.minute + 40
        occurred = timezone.make_aware(
            datetime.combine(today, time(minute // 60, minute % 60)),
            timezone.get_current_timezone(),
        )
        AttendanceEvent.objects.create(
            employee=employee,
            occurred_at=occurred,
            event_type="in",
            source="device_import",
            device_reference=f"SAMPLE-DEVICE-{shift.id}",
        )

    def _user(self, email, first, last, role, client=None, employee=None):
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.create_user(
                email=email,
                password=PASSWORD,
                first_name=first,
                last_name=last,
                role=role,
                client=client,
                employee=employee,
                is_demo=True,
            )
        return user

    def _skill(self, employee, skill, rate):
        Qualification.objects.get_or_create(employee=employee, skill=skill)
        PayProfile.objects.update_or_create(employee=employee, defaults={"hourly_rate": rate, "currency": "GHS"})

    def _available_weaver(self, client, site, position, today):
        employee = Employee.objects.update_or_create(
            agency_employee_number="SN-1004",
            defaults={"first_name": "Abena", "last_name": "Boateng", "status": "active", "is_demo": True},
        )[0]
        EmployeeIdentifier.objects.get_or_create(
            employee=employee,
            kind="ghana_card",
            defaults={"ciphertext": encrypt("SAMPLE-NOT-A-REAL-ID-SN-1004"), "is_synthetic": True},
        )
        EmploymentContract.objects.update_or_create(
            employee=employee,
            is_current=True,
            defaults={
                "legal_employer_kind": LegalEmployerKind.AGENCY,
                "legal_employer_client": None,
                "starts_on": today - timedelta(days=20),
                "ends_on": None,
            },
        )
        Deployment.objects.update_or_create(
            employee=employee,
            is_current=True,
            defaults={
                "client": client,
                "site": site["site"],
                "department": site["department"],
                "position": position,
                "starts_on": today - timedelta(days=10),
            },
        )
        self._skill(employee, "weaving", Decimal("20.00"))
