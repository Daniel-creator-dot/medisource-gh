from django.urls import path

from modules.workforce.profile import EmployeeProfileView
from modules.workforce.views import EmployeeListView, MyEmploymentView

urlpatterns = [
    path("employees/", EmployeeListView.as_view(), name="employees"),
    path("employees/<uuid:employee_id>/", EmployeeProfileView.as_view(), name="employee-profile"),
    path("me/employment/", MyEmploymentView.as_view(), name="my-employment"),
]
