from django.urls import path

from modules.finance.views import BooksView, FinanceView, PostWeekView, ReceiptView, RebuildInvoicesView

urlpatterns = [
    path("finance/", FinanceView.as_view(), name="finance"),
    path("finance/worksheets/rebuild/", RebuildInvoicesView.as_view(), name="finance-rebuild"),
    path("accounting/", BooksView.as_view(), name="books"),
    path("accounting/post-week/", PostWeekView.as_view(), name="post-week"),
    path("accounting/receipts/", ReceiptView.as_view(), name="receipts"),
]
