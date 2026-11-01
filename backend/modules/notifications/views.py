from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.api import ok
from common.pagination import EnvelopePagination
from modules.audit.services import record_audit
from modules.notifications.models import ContactInquiry, Notification
from modules.notifications.serializers import ContactInquirySerializer, NotificationSerializer
from modules.notifications.throttles import ContactRateThrottle


class NotificationListView(APIView):
    def get(self, request):
        queryset = Notification.objects.filter(user=request.user)
        paginator = EnvelopePagination()
        page = paginator.paginate_queryset(queryset, request)
        return paginator.get_paginated_response(NotificationSerializer(page, many=True).data)


class NotificationReadView(APIView):
    def patch(self, request, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return ok(NotificationSerializer(notification).data)


class ContactInquiryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def post(self, request):
        serializer = ContactInquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inquiry = ContactInquiry.objects.create(
            **serializer.validated_data,
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        record_audit(
            action="support.inquiry_created",
            resource_type="contact_inquiry",
            resource_id=inquiry.id,
            request=request,
        )
        return ok({"received": True}, status=201)
