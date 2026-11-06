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


@pytest.mark.django_db
def test_ledger_position_classifies_posted_lines_and_refuses_a_profit_figure(api):
    call_command("seed_demo")
    auth(api, "client.ashanti@sample.sraj.test")
    assert api.get("/api/v1/accounting/position/").status_code == 403
    auth(api, "nova.owner@sample.sraj.test")
    api.post("/api/v1/accounting/post-week/", {}, format="json")
    position = api.get("/api/v1/accounting/position/").json()["data"]
    assert position["trial_balance_balanced"] is True
    assert position["assets"] == "3176.20"
    assert position["liabilities"] == "606.00"
    assert position["equity"] == "2500.00"
    assert position["recognized_fee_revenue"] == "70.20"
    assert position["expenses"] == "0.00"
    assert position["operating_profit"] is None


@pytest.mark.django_db
def test_a_draft_stays_out_of_the_trial_balance_until_it_is_posted_and_a_posted_journal_is_reversed(api):
    call_command("seed_demo")
    auth(api, "client.ashanti@sample.sraj.test")
    refused = api.post("/api/v1/accounting/journals/", {"entry_date": "2026-11-06", "memo": "Client draft", "lines": []}, format="json")
    assert refused.status_code == 403
    auth(api, "nova.owner@sample.sraj.test")
    from django.utils import timezone

    today = timezone.localdate().isoformat()
    posted = api.post("/api/v1/accounting/post-week/", {}, format="json")
    assert posted.json()["data"]["trial_balance"]["total_debit"] == "3176.20"
    period_id = posted.json()["data"]["periods"][0]["id"]
    assert posted.json()["data"]["periods"][0]["status"] == "open"
    draft = api.post(
        "/api/v1/accounting/journals/",
        {
            "entry_date": today,
            "memo": "Sample manual draft",
            "lines": [{"code": "1000", "debit": "10.00", "credit": "0"}, {"code": "1000", "debit": "1.00", "credit": "0"}],
        },
        format="json",
    )
    assert draft.status_code == 201
    draft_id = draft.json()["data"]["id"]
    unbalanced = api.post(f"/api/v1/accounting/journals/{draft_id}/post/", {}, format="json")
    assert unbalanced.status_code == 400
    assert api.get("/api/v1/accounting/").json()["data"]["trial_balance"]["total_debit"] == "3176.20"
    balanced = api.post(
        "/api/v1/accounting/journals/",
        {
            "entry_date": today,
            "memo": "Sample manual transfer",
            "lines": [{"code": "1000", "debit": "10.00", "credit": "0"}, {"code": "3000", "debit": "0", "credit": "10.00"}],
        },
        format="json",
    )
    entry_id = balanced.json()["data"]["id"]
    accepted = api.post(f"/api/v1/accounting/journals/{entry_id}/post/", {}, format="json")
    assert accepted.status_code == 200
    assert accepted.json()["data"]["trial_balance"]["total_debit"] == "3186.20"
    original = JournalEntry.objects.get(pk=entry_id)
    original_lines = list(JournalLine.objects.filter(entry=original).values_list("debit", "credit"))
    reversed_books = api.post(f"/api/v1/accounting/journals/{entry_id}/reverse/", {}, format="json")
    assert reversed_books.status_code == 200
    books = reversed_books.json()["data"]
    assert books["trial_balance"]["balanced"] is True
    assert books["trial_balance"]["total_debit"] == "3196.20"
    cash = next(row for row in books["trial_balance"]["rows"] if row["code"] == "1000")
    assert cash["debit"] == "2510.00"
    assert cash["credit"] == "10.00"
    original.refresh_from_db()
    assert list(JournalLine.objects.filter(entry=original).values_list("debit", "credit")) == original_lines
    assert api.post(f"/api/v1/accounting/journals/{entry_id}/reverse/", {}, format="json").status_code == 400
    closed = api.post(f"/api/v1/accounting/periods/{period_id}/", {"status": "closed"}, format="json")
    assert closed.status_code == 200
    blocked = api.post("/api/v1/accounting/post-week/", {}, format="json")
    assert blocked.status_code == 400
    assert blocked.json()["error"]["code"] == "period_closed"
