from django.urls import path

from modules.notifications.views import ContactInquiryView, NotificationListView, NotificationReadView

urlpatterns = [
    path("account/notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "account/notifications/<uuid:notification_id>/",
        NotificationReadView.as_view(),
        name="notification-read",
    ),
    path("support/inquiries/", ContactInquiryView.as_view(), name="contact-inquiry"),
]
