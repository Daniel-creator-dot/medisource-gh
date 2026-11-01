import os

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from modules.audit.services import record_audit
from modules.catalog.constants import DEMO_LABEL
from modules.catalog.models import (
    Category,
    CategoryPolicy,
    Listing,
    ListingStatus,
    MasterProduct,
    Supplier,
    SupplierVerification,
)
from modules.identity.models import PlatformRole, User
from modules.organizations.models import MembershipRole, OrganizationType
from modules.organizations.services import create_organization

ELIGIBLE = (
    "Development policy for eligible non-prescription supplies. "
    "This text is not a regulatory approval."
)
CLOSED = (
    "Checkout stays closed until a regulator-specific policy is configured. "
    "This is not an FDA, Pharmacy Council, or HeFRA decision."
)

CATEGORIES = [
    ("medical-consumables", "Medical consumables", "Everyday clinical consumables such as swabs and prep pads.", True, False),
    ("medical-equipment", "Medical equipment", "Reusable clinical equipment for facilities.", True, False),
    ("surgical-instruments", "Surgical instruments", "Instruments for theatre and procedure rooms.", True, False),
    ("laboratory-supplies", "Laboratory supplies", "Consumables used by diagnostic laboratories.", True, False),
    ("diagnostic-equipment", "Diagnostic equipment", "Devices used to measure or observe clinical signs.", True, False),
    ("hospital-furniture", "Hospital furniture", "Furniture designed for care settings.", True, False),
    ("ppe", "PPE", "Personal protective equipment for staff and visitors.", True, False),
    ("orthopedic-supplies", "Orthopedic supplies", "Supports and related orthopedic consumables.", True, False),
    ("rehabilitation-equipment", "Rehabilitation equipment", "Mobility and rehabilitation equipment.", True, False),
    ("authorized-pharmaceuticals", "Authorized pharmaceuticals", "Reserved for products that a future policy may allow. Nothing in this category can be checked out.", False, True),
    ("other-healthcare-supplies", "Other healthcare supplies", "Items that still need a category policy before they can be sold.", False, False),
]

PRODUCTS = [
    {
        "slug": "nitrile-examination-gloves",
        "name": "Nitrile examination gloves",
        "category": "ppe",
        "manufacturer": "SampleMed Industries",
        "brand": "SampleMed",
        "description": "Powder-free nitrile examination gloves for general clinical contact.",
        "specification": "Fictional specification for a size medium glove, 100 pieces in a box.",
        "pack_size": "Box of 100",
        "unit_of_measure": "box",
        "listings": [
            ("harbour", "SM-GLOVE-100", "46.00", 240, 2, 2),
            ("savanna", "SV-GLOVE-100", "49.50", 120, 1, 4),
        ],
    },
    {
        "slug": "surgical-face-masks",
        "name": "Surgical face masks",
        "category": "ppe",
        "manufacturer": "SampleMed Industries",
        "brand": "SampleMed",
        "description": "Three-layer disposable face masks for routine clinical use.",
        "specification": "Fictional ear-loop mask, 50 pieces in a box.",
        "pack_size": "Box of 50",
        "unit_of_measure": "box",
        "listings": [("harbour", "SM-MASK-50", "28.00", 400, 1, 2)],
    },
    {
        "slug": "alcohol-prep-pads",
        "name": "Alcohol prep pads",
        "category": "medical-consumables",
        "manufacturer": "Fictional Labs Co.",
        "brand": "Fictional Labs",
        "description": "Single-use skin prep pads for procedures that need a clean skin surface.",
        "specification": "Fictional 70 percent isopropyl pad, 200 pieces in a box.",
        "pack_size": "Box of 200",
        "unit_of_measure": "box",
        "listings": [("harbour", "FL-PREP-200", "36.00", 180, 1, 3)],
    },
    {
        "slug": "digital-clinical-thermometer",
        "name": "Digital clinical thermometer",
        "category": "diagnostic-equipment",
        "manufacturer": "Example Device Works",
        "brand": "Example Device",
        "description": "Handheld digital thermometer for ward and clinic temperature checks.",
        "specification": "Fictional oral and axillary device with a protective case.",
        "pack_size": "Each",
        "unit_of_measure": "each",
        "listings": [("savanna", "ED-THERM-1", "85.00", 60, 1, 5)],
    },
    {
        "slug": "fingertip-pulse-oximeter",
        "name": "Fingertip pulse oximeter",
        "category": "diagnostic-equipment",
        "manufacturer": "Example Device Works",
        "brand": "Example Device",
        "description": "Fingertip device for spot checks of oxygen saturation and pulse.",
        "specification": "Fictional LED display device supplied with a lanyard.",
        "pack_size": "Each",
        "unit_of_measure": "each",
        "listings": [
            ("harbour", "ED-OX-1", "240.00", 40, 1, 5),
            ("savanna", "SV-OX-1", "255.00", 25, 1, 6),
        ],
    },
    {
        "slug": "manual-wheelchair",
        "name": "Manual wheelchair",
        "category": "rehabilitation-equipment",
        "manufacturer": "Example Device Works",
        "brand": "Example Device",
        "description": "Self-propelled wheelchair for facility transport and short-term loan.",
        "specification": "Fictional 18 inch seat, swing-away footrests, indoor and outdoor tyres.",
        "pack_size": "Each",
        "unit_of_measure": "each",
        "listings": [("savanna", "ED-CHAIR-18", "1450.00", 12, 1, 10)],
    },
    {
        "slug": "overbed-table",
        "name": "Overbed table",
        "category": "hospital-furniture",
        "manufacturer": "SampleMed Industries",
        "brand": "SampleMed",
        "description": "Height-adjustable overbed table for a ward bed.",
        "specification": "Fictional laminate top with a locking castor base.",
        "pack_size": "Each",
        "unit_of_measure": "each",
        "listings": [("savanna", "SM-TABLE-1", "980.00", 15, 1, 12)],
    },
    {
        "slug": "sterile-pipette-tips",
        "name": "Sterile pipette tips 200 microlitre",
        "category": "laboratory-supplies",
        "manufacturer": "Fictional Labs Co.",
        "brand": "Fictional Labs",
        "description": "Racked sterile tips for routine liquid handling.",
        "specification": "Fictional 96-tip rack, filtered, sterile.",
        "pack_size": "Rack of 96",
        "unit_of_measure": "rack",
        "listings": [("harbour", "FL-TIP-200", "62.00", 300, 2, 4)],
    },
]


class Command(BaseCommand):
    help = "Load labelled fictional catalogue and demo accounts. Refuses to run when DEBUG is false."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=os.environ.get("SEED_DEMO_PASSWORD", "Demo-Only-Change-Me-1"),
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not settings.FORCE_SEED_DEMO:
            raise CommandError("Refusing to seed demo data while DEBUG is false.")
        password = options["password"]
        try:
            validate_password(password)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc

        with transaction.atomic():
            categories = self._categories()
            harbour_user = self._user(
                email="kofi.supplier@sample.medisource.test",
                password=password,
                first_name="Kofi",
                last_name="Mensah",
                role=PlatformRole.SUPPLIER,
            )
            savanna_user = self._user(
                email="ama.supplier@sample.medisource.test",
                password=password,
                first_name="Ama",
                last_name="Boateng",
                role=PlatformRole.SUPPLIER,
            )
            self._user(
                email="ada.customer@sample.medisource.test",
                password=password,
                first_name="Ada",
                last_name="Owusu",
                role=PlatformRole.CUSTOMER,
            )
            self._user(
                email="yaw.admin@sample.medisource.test",
                password=password,
                first_name="Yaw",
                last_name="Darko",
                role=PlatformRole.PLATFORM_ADMIN,
                is_staff=True,
            )
            harbour = self._supplier(
                owner=harbour_user,
                slug="sample-harbour-clinic-supplies",
                org_slug="sample-harbour-clinic-supplies-org",
                name="Sample: Harbour Clinic Supplies",
                summary="Fictional Accra wholesaler used to demonstrate the public catalogue. " + DEMO_LABEL,
                city="Accra",
                region="Greater Accra",
                warehouse="Sample warehouse — Accra",
                zones=["Greater Accra", "Central", "Eastern"],
            )
            savanna = self._supplier(
                owner=savanna_user,
                slug="sample-savanna-equipment-desk",
                org_slug="sample-savanna-equipment-desk-org",
                name="Sample: Savanna Equipment Desk",
                summary="Fictional Kumasi equipment desk used to demonstrate a second supplier. " + DEMO_LABEL,
                city="Kumasi",
                region="Ashanti",
                warehouse="Sample warehouse — Kumasi",
                zones=["Ashanti", "Bono", "Greater Accra"],
            )
            suppliers = {"harbour": harbour, "savanna": savanna}
            for product in PRODUCTS:
                self._product(product, categories, suppliers)
            record_audit(action="catalog.demo_seeded", resource_type="catalog", metadata={"products": len(PRODUCTS)})

        self.stdout.write(self.style.WARNING("Sample data only. These accounts and listings are fictional."))
        self.stdout.write(f"Demo password for every sample account: {password}")
        self.stdout.write("ada.customer@sample.medisource.test")
        self.stdout.write("kofi.supplier@sample.medisource.test")
        self.stdout.write("ama.supplier@sample.medisource.test")
        self.stdout.write("yaw.admin@sample.medisource.test")

    def _categories(self):
        categories = {}
        for index, (slug, name, description, checkout, requires) in enumerate(CATEGORIES, start=1):
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "sort_order": index},
            )
            CategoryPolicy.objects.update_or_create(
                category=category,
                defaults={
                    "checkout_enabled": checkout,
                    "requires_authorization": requires,
                    "policy_reference": ELIGIBLE if checkout else CLOSED,
                },
            )
            categories[slug] = category
        return categories

    def _user(self, *, email, password, first_name, last_name, role, is_staff=False):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "platform_role": role,
                "is_demo_account": True,
                "is_staff": is_staff,
                "email_verified": True,
            },
        )
        if created:
            user.set_password(password)
            user.save()
        return user

    def _supplier(self, *, owner, slug, org_slug, name, summary, city, region, warehouse, zones):
        from modules.organizations.models import Organization

        organization = Organization.objects.filter(slug=org_slug).first()
        if organization is None:
            organization = create_organization(
                name=name,
                slug=org_slug,
                org_type=OrganizationType.SUPPLIER,
                owner=owner,
                role=MembershipRole.OWNER,
            )
        supplier, _ = Supplier.objects.update_or_create(
            slug=slug,
            defaults={
                "organization": organization,
                "display_name": name,
                "summary": summary,
                "city": city,
                "region": region,
                "verification_status": SupplierVerification.DEMO,
                "verified_at": None,
                "is_demo": True,
                "internal_notes": "Demo account. No bank details, licences, or private trading terms are stored here.",
            },
        )
        supplier._seed_warehouse = warehouse
        supplier._seed_zones = zones
        return supplier

    def _product(self, spec, categories, suppliers):
        product, _ = MasterProduct.objects.update_or_create(
            slug=spec["slug"],
            defaults={
                "category": categories[spec["category"]],
                "name": spec["name"],
                "manufacturer": spec["manufacturer"],
                "brand": spec["brand"],
                "description": spec["description"],
                "specification": spec["specification"],
                "pack_size": spec["pack_size"],
                "unit_of_measure": spec["unit_of_measure"],
                "regulatory_notes": DEMO_LABEL,
                "is_demo": True,
            },
        )
        for key, sku, price, stock, moq, lead in spec["listings"]:
            supplier = suppliers[key]
            Listing.objects.update_or_create(
                supplier=supplier,
                sku=sku,
                defaults={
                    "master_product": product,
                    "price_amount": price,
                    "currency": "GHS",
                    "stock_quantity": stock,
                    "minimum_order_quantity": moq,
                    "lead_time_days": lead,
                    "warehouse_name": supplier._seed_warehouse,
                    "delivery_zones": supplier._seed_zones,
                    "status": ListingStatus.ACTIVE,
                    "is_demo": True,
                },
            )
