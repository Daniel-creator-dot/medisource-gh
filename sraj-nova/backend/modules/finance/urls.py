from django.urls import path

from modules.finance.views import FinanceView, RebuildInvoicesView

urlpatterns = [
    path("finance/", FinanceView.as_view(), name="finance"),
    path("finance/worksheets/rebuild/", RebuildInvoicesView.as_view(), name="finance-rebuild"),
]
