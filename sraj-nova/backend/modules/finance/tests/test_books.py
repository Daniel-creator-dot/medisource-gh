from decimal import Decimal

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from modules.finance.models import JournalEntry, JournalLine
from modules.identity.models import User


def auth(api, email):
    user = User.objects.get(email=email)
    access = str(RefreshToken.for_user(user).access_token)
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return api


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_client_cannot_open_the_books(api):
    call_command("seed_demo")
    auth(api, "client.ashanti@sample.sraj.test")
    assert api.get("/api/v1/accounting/").status_code == 403
    assert api.post("/api/v1/accounting/post-week/", {}, format="json").status_code == 403


@pytest.mark.django_db
def test_posting_balances_and_repost_reverses_instead_of_editing(api):
    from datetime import timedelta

    from django.utils import timezone

    call_command("seed_demo")
    auth(api, "nova.owner@sample.sraj.test")
    first = api.post("/api/v1/accounting/post-week/", {}, format="json")
    assert first.status_code == 200
    books = first.json()["data"]
    assert books["trial_balance"]["balanced"] is True
    assert books["trial_balance"]["total_debit"] == books["trial_balance"]["total_credit"]
    assert books["trial_balance"]["total_debit"] == "3176.20"
    start = timezone.localdate()
    start = start - timedelta(days=start.weekday())
    original = JournalEntry.objects.get(memo=f"Invoice Sample Ashanti Textile Works week {start.isoformat()}")
    original_debits = list(JournalLine.objects.filter(entry=original).values_list("debit", "credit"))
    second = api.post("/api/v1/accounting/post-week/", {}, format="json")
    assert second.status_code == 200
    original.refresh_from_db()
    assert list(JournalLine.objects.filter(entry=original).values_list("debit", "credit")) == original_debits
    assert JournalEntry.objects.filter(reverses=original).exists()
    assert second.json()["data"]["trial_balance"]["balanced"] is True


@pytest.mark.django_db
def test_receipt_reduces_receivable_and_rejects_an_overpayment(api):
    call_command("seed_demo")
    auth(api, "nova.ops@sample.sraj.test")
    api.post("/api/v1/accounting/post-week/", {}, format="json")
    invoice_id = next(row["id"] for row in api.get("/api/v1/accounting/").json()["data"]["open_invoices"] if "Ashanti" in row["client_name"])
    refused = api.post("/api/v1/accounting/receipts/", {"invoice_id": invoice_id, "amount": "9999.00", "reference": "SAMPLE-RCPT-1"}, format="json")
    assert refused.status_code == 400
    accepted = api.post("/api/v1/accounting/receipts/", {"invoice_id": invoice_id, "amount": "100.00", "reference": "SAMPLE-RCPT-1"}, format="json")
    assert accepted.status_code == 201
    books = accepted.json()["data"]
    cash = next(row for row in books["trial_balance"]["rows"] if row["code"] == "1000")
    receivable = next(row for row in books["trial_balance"]["rows"] if row["code"] == "1100")
    assert cash["debit"] == "2600.00"
    assert receivable["debit"] == "676.20"
    assert receivable["credit"] == "100.00"
    assert books["trial_balance"]["balanced"] is True
    ashanti = next(row for row in books["aging"] if "Ashanti" in row["client_name"])
    assert ashanti["outstanding"] == "437.60"
    assert Decimal(books["trial_balance"]["total_debit"]) == Decimal(books["trial_balance"]["total_credit"])
