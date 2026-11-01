import pytest

from conftest import post_json
from modules.audit.models import AuditLog
from modules.notifications.models import ContactInquiry


@pytest.mark.django_db
def test_contact_inquiry_is_stored_without_a_session(api, csrf_token):
    response = post_json(
        api,
        "/api/v1/support/inquiries/",
        {
            "name": "Ama Serwaa",
            "email": "ama@example.com",
            "organization_name": "Sample Clinic",
            "topic": "support",
            "message": "Please tell me when supplier registration will open for Accra wholesalers.",
        },
        csrf_token,
    )
    assert response.status_code == 201
    assert ContactInquiry.objects.count() == 1
    assert AuditLog.objects.filter(action="support.inquiry_created").exists()

    short = post_json(
        api,
        "/api/v1/support/inquiries/",
        {
            "name": "Ama Serwaa",
            "email": "ama@example.com",
            "topic": "support",
            "message": "Too short",
        },
        csrf_token,
    )
    assert short.status_code == 400
