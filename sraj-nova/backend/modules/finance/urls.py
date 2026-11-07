from django.urls import path

from modules.finance.views import (
    BooksView,
    FinanceView,
    LedgerPositionView,
    ManualJournalView,
    PeriodStatusView,
    PostDraftView,
    PostWeekView,
    ReceiptView,
    RebuildInvoicesView,
    TaxSettingsView,
    ReverseJournalView,
)

urlpatterns = [
    path("finance/", FinanceView.as_view(), name="finance"),
    path("settings/tax/", TaxSettingsView.as_view(), name="tax-settings"),
    path("finance/worksheets/rebuild/", RebuildInvoicesView.as_view(), name="finance-rebuild"),
    path("accounting/", BooksView.as_view(), name="books"),
    path("accounting/position/", LedgerPositionView.as_view(), name="ledger-position"),
    path("accounting/post-week/", PostWeekView.as_view(), name="post-week"),
    path("accounting/receipts/", ReceiptView.as_view(), name="receipts"),
    path("accounting/journals/", ManualJournalView.as_view(), name="manual-journal"),
    path("accounting/journals/<uuid:entry_id>/post/", PostDraftView.as_view(), name="post-draft"),
    path("accounting/journals/<uuid:entry_id>/reverse/", ReverseJournalView.as_view(), name="reverse-journal"),
    path("accounting/periods/<uuid:period_id>/", PeriodStatusView.as_view(), name="period-status"),
]
