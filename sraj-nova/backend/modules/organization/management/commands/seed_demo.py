from datetime import datetime, time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from decimal import Decimal

from common.crypto import encrypt
from modules.finance.ledger import post_opening_cash
from modules.finance.models import CashMovement
from modules.finance.services import rebuild_week_invoices
from modules.identity.models import AgencyRole, User
from modules.operations.models import AttendanceEvent, OperationalAlert, ShiftAssignment, StaffingRequest
from modules.organization.models import Agency, Client, ClientSite, Department, JobPosition, ServiceContract
from modules.workforce.models import (
    Applicant,
    ApplicantStatus,
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
        today = timezone.localdate()
        if Agency.objects.filter(legal_name="SRAJ NOVA Ltd", seeded_on=today).exists():
            self.stdout.write("Demonstration data is already loaded for today.")
            return
        with transaction.atomic():
            self._load()
            Agency.objects.filter(legal_name="SRAJ NOVA Ltd").update(seeded_on=today)
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
        ashanti = self._client("sample-ashanti-textile", "Sample Ashanti Cement Works", "Cement")
        takoradi = self._client("sample-tema-logistics", "Sample Takoradi Cement Works", "Cement")
        today = timezone.localdate()
        ashanti_site, ashanti_departments = self._plant(ashanti, "Ashanti Grinding Plant", "Tema", "Greater Accra")
        takoradi_site, takoradi_departments = self._plant(takoradi, "Takoradi Grinding Plant", "Takoradi", "Western")
        mill = self._position(ashanti, "Mill operator", "milling", "Weaving operator")
        packer = self._position(ashanti, "Packing operator", "packing", "")
        laboratory = self._position(ashanti, "Laboratory assistant", "quality", "")
        fitter = self._position(ashanti, "Fitter", "mechanical", "")
        takoradi_packer = self._position(takoradi, "Packing operator", "packing", "Dispatch loader")
        people = [
            ("SN-1001", "Ama", "Mensah", ashanti, ashanti_site, ashanti_departments["Production"], mill, LegalEmployerKind.AGENCY, None, time(6, 0), "on_time", "milling", Decimal("20.00")),
            ("SN-1002", "Kofi", "Boateng", ashanti, ashanti_site, ashanti_departments["Mechanical"], fitter, LegalEmployerKind.CLIENT, ashanti, time(6, 0), "late", "mechanical", Decimal("20.00")),
            ("SN-1003", "Esi", "Owusu", ashanti, ashanti_site, ashanti_departments["Quality"], laboratory, LegalEmployerKind.AGENCY, None, time(6, 0), "absent", "quality", Decimal("20.00")),
            ("SN-2001", "Yaw", "Darko", takoradi, takoradi_site, takoradi_departments["Packing"], takoradi_packer, LegalEmployerKind.AGENCY, None, time(7, 0), "on_time", "packing", Decimal("18.00")),
        ]
        for number, first, last, client, site, department, position, employer, employer_client, start, attendance, skill, rate in people:
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
                    "site": site,
                    "department": department,
                    "position": position,
                    "starts_on": today - timedelta(days=30),
                },
            )
            ShiftAssignment.objects.filter(employee=employee).update(client=client, site=site, department=department, position=position)
            shift = ShiftAssignment.objects.update_or_create(
                employee=employee,
                work_date=today,
                defaults={
                    "client": client,
                    "site": site,
                    "department": department,
                    "position": position,
                    "starts_at": start,
                    "ends_at": time(14, 0),
                },
            )[0]
            self._punch(employee, today, start, attendance, shift)
            self._skill(employee, skill, rate)
        self._available_fitter(ashanti, ashanti_site, ashanti_departments["Mechanical"], fitter, today)
        open_posts = list(
            ShiftAssignment.objects.filter(client=ashanti, employee__isnull=True, work_date=today).order_by("created_at")
        )
        if open_posts:
            open_post = open_posts[0]
            open_post.site = ashanti_site
            open_post.department = ashanti_departments["Mechanical"]
            open_post.position = fitter
            open_post.starts_at = time(14, 0)
            open_post.ends_at = time(22, 0)
            open_post.save()
            ShiftAssignment.objects.filter(pk__in=[row.pk for row in open_posts[1:]]).delete()
        else:
            ShiftAssignment.objects.create(
                client=ashanti,
                site=ashanti_site,
                department=ashanti_departments["Mechanical"],
                position=fitter,
                employee=None,
                work_date=today,
                starts_at=time(14, 0),
                ends_at=time(22, 0),
            )
        ShiftAssignment.objects.filter(client=ashanti, employee__isnull=True).exclude(work_date=today).update(
            site=ashanti_site,
            department=ashanti_departments["Mechanical"],
            position=fitter,
        )
        self._contract(ashanti, "Sample cement labour agreement", Decimal("0.1200"), today - timedelta(days=200), today + timedelta(days=20))
        self._contract(takoradi, "Sample cement labour agreement", Decimal("0.1000"), today - timedelta(days=100), today + timedelta(days=200))
        request = StaffingRequest.objects.filter(client=ashanti, is_demo=True).order_by("created_at").first()
        if request is None:
            StaffingRequest.objects.create(
                client=ashanti,
                site=ashanti_site,
                title="Sample request for two night packers",
                headcount=2,
                status="pending",
                is_demo=True,
            )
        else:
            request.site = ashanti_site
            request.title = "Sample request for two night packers"
            request.headcount = 2
            request.status = "pending"
            request.save()
        alert = OperationalAlert.objects.filter(client=ashanti).order_by("created_at").first()
        if alert is None:
            OperationalAlert.objects.create(
                message="Sample afternoon shift in Mechanical has no assigned fitter.",
                client=ashanti,
                severity="warning",
                is_open=True,
            )
        else:
            alert.message = "Sample afternoon shift in Mechanical has no assigned fitter."
            alert.is_open = True
            alert.save()
        Applicant.objects.get_or_create(
            first_name="Kojo",
            last_name="Nyarko",
            is_demo=True,
            defaults={
                "phone": "",
                "skill": "packing",
                "site": ashanti_site,
                "department": ashanti_departments["Packing"],
                "position": packer,
                "status": ApplicantStatus.APPLIED,
                "note": "Sample application for the packing department. Not a real person.",
            },
        )
        for site in (ashanti_site, takoradi_site):
            for name in ("Weaving", "Dispatch"):
                stale = Department.objects.filter(site=site, name=name).first()
                if stale is not None and not stale.shifts.exists() and not stale.deployments.exists():
                    stale.delete()
        owner = self._user("nova.owner@sample.sraj.test", "Nana", "Sarpong", AgencyRole.AGENCY_OWNER)
        self._user("nova.ops@sample.sraj.test", "Akua", "Frimpong", AgencyRole.AGENCY_OPERATIONS)
        self._user("nova.finance@sample.sraj.test", "Yaa", "Asante", AgencyRole.AGENCY_FINANCE)
        self._user("client.ashanti@sample.sraj.test", "Kojo", "Asare", AgencyRole.CLIENT_USER, client=ashanti)
        worker = Employee.objects.get(agency_employee_number="SN-1001")
        self._user("worker.ama@sample.sraj.test", "Ama", "Mensah", AgencyRole.EMPLOYEE, employee=worker)
        owner.is_demo = True
        owner.save(update_fields=["is_demo"])
        ama = Employee.objects.get(agency_employee_number="SN-1001")
        certificate = Certification.objects.filter(employee=ama).order_by("created_at").first()
        if certificate is None:
            Certification.objects.create(employee=ama, name="Sample mill safety certificate", expires_on=today + timedelta(days=200))
        else:
            certificate.name = "Sample mill safety certificate"
            certificate.expires_on = today + timedelta(days=200)
            certificate.save()
        LeaveRequest.objects.get_or_create(employee=ama, starts_on=today + timedelta(days=14), ends_on=today + timedelta(days=16), defaults={"status": "approved"})
        hiring = RecruitmentEvent.objects.filter(employee=ama).order_by("created_at").first()
        if hiring is None:
            RecruitmentEvent.objects.create(
                employee=ama,
                summary="Sample application accepted for a mill operator role.",
                occurred_on=today - timedelta(days=45),
            )
        else:
            hiring.summary = "Sample application accepted for a mill operator role."
            hiring.save()
        note = HrNote.objects.filter(employee=ama, visibility="standard").first()
        if note is None:
            HrNote.objects.create(employee=ama, visibility="standard", body="Sample orientation completed at the grinding plant.")
        else:
            note.body = "Sample orientation completed at the grinding plant."
            note.save()
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
        post_opening_cash(Decimal("2500.00"), today)

    def _client(self, slug, name, sector):
        return Client.objects.update_or_create(
            slug=slug,
            defaults={"legal_name": name, "sector": sector, "status": "active", "is_demo": True, "demo_label": DEMO},
        )[0]

    def _plant(self, client, name, city, region):
        site = client.sites.order_by("created_at").first()
        if site is None:
            site = ClientSite.objects.create(client=client, name=name, city=city, region=region, is_demo=True)
        else:
            site.name = name
            site.city = city
            site.region = region
            site.is_demo = True
            site.save(update_fields=["name", "city", "region", "is_demo", "updated_at"])
        departments = {}
        for label in ("Production", "Packing", "Quality", "Mechanical", "Electrical", "Health and safety"):
            departments[label] = Department.objects.get_or_create(site=site, name=label)[0]
        return site, departments

    def _position(self, client, title, skill, previous_title):
        row = JobPosition.objects.filter(client=client, title=title).first()
        if row is None and previous_title:
            row = JobPosition.objects.filter(client=client, title=previous_title).first()
        if row is None:
            return JobPosition.objects.create(client=client, title=title, required_skill=skill)
        row.title = title
        row.required_skill = skill
        row.save(update_fields=["title", "required_skill", "updated_at"])
        return row

    def _contract(self, client, title, rate, starts_on, ends_on):
        row = ServiceContract.objects.filter(client=client).order_by("-ends_on").first()
        if row is None:
            ServiceContract.objects.create(
                client=client,
                title=title,
                billing_model="cost_plus",
                management_fee_rate=rate,
                starts_on=starts_on,
                ends_on=ends_on,
                is_demo=True,
            )
            return
        row.title = title
        row.billing_model = "cost_plus"
        row.management_fee_rate = rate
        row.starts_on = starts_on
        row.ends_on = ends_on
        row.is_demo = True
        row.save()

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

    def _available_fitter(self, client, site, department, position, today):
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
                "site": site,
                "department": department,
                "position": position,
                "starts_on": today - timedelta(days=10),
            },
        )
        self._skill(employee, "mechanical", Decimal("20.00"))
