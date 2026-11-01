from modules.notifications.models import Notification


def notify_welcome(user) -> Notification:
    return Notification.objects.create(
        user=user,
        title="Welcome to MediSource GH",
        body=(
            "Your customer account is ready. Verify your email to finish setting it up. "
            "Catalogue rows marked as sample data are fictional and cannot be purchased."
        ),
    )
