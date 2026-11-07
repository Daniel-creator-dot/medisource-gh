from django.urls import path

from modules.workforce.hr_views import AddStaffView, ApplicantStatusView, ApplicantsView, HireApplicantView
from modules.workforce.profile import EmployeeProfileView
from modules.workforce.views import EmployeeListView, MyEmploymentView

urlpatterns = [
    path("employees/", EmployeeListView.as_view(), name="employees"),
    path("hr/staff/", AddStaffView.as_view(), name="add-staff"),
    path("hr/applicants/", ApplicantsView.as_view(), name="applicants"),
    path("hr/applicants/<uuid:applicant_id>/status/", ApplicantStatusView.as_view(), name="applicant-status"),
    path("hr/applicants/<uuid:applicant_id>/hire/", HireApplicantView.as_view(), name="hire-applicant"),
    path("employees/<uuid:employee_id>/", EmployeeProfileView.as_view(), name="employee-profile"),
    path("me/employment/", MyEmploymentView.as_view(), name="my-employment"),
]
