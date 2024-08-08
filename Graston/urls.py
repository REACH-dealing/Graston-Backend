from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from Graston.settings import STATIC_ROOT, STATIC_URL
from users.views import *
from graston_sessions.views import *

urlpatterns = [
    # _________________________________ admin end point ____________________________________________#
    path("admin", admin.site.urls),
    # __________________________ API auto documentation end points _________________________________#
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # ____________________________ User authentication end points ___________________________________#
    path(
        "auth/register/patient",
        PatientRegisterView.as_view(),
        name="patient_register",
    ),
    path(
        "auth/register/nurse",
        NurseRegisterView.as_view(),
        name="nurse_register",
    ),
    path(
        "auth/send-otp2email/<int:user_id>",
        VerifyAccount.as_view({"get": "send_otp2email"}),
        name="send_otp2email",
    ),
    path(
        "auth/verify-otp/<int:user_id>",
        VerifyAccount.as_view({"post": "verify_otp"}),
        name="verify_otp",
    ),
    path(
        "auth/login",
        LoginView.as_view({"post": "login"}),
        name="login",
    ),
    path(
        "auth/logout",
        LogoutView.as_view({"post": "logout"}),
        name="logout",
    ),
    path(
        "auth/user",
        UserView.as_view({"get": "retrieve"}),
        name="logged_in_user_data",
    ),
    # path(
    #     "auth/refresh-token",
    #     RefreshTokenView.as_view({"post": "refresh_token"}),
    #     name="refresh_token",
    # ),
    path(
        "auth/delete-account/<pk>",
        SoftDeleteAccountView.as_view(),
        name="delete_account",
    ),
    path(
        "auth/reactivate-account/<pk>",
        RectivateAccountView.as_view(),
        name="reactivate_account",
    ),
    path(
        "auth/change-password",
        PasswordChangeView.as_view(),
        name="change_password",
    ),
    path(
        "auth/check-password",
        CheckPasswordView.as_view(),
        name="check_password",
    ),
    path(
        "auth/change-email",
        ChangeEmailView.as_view(),
        name="change_email",
    ),
    path(
        "auth/forget-password",
        ForgetPasswordView.as_view(),
        name="forget_password",
    ),
    path(
        "auth/forget-password/verify-otp/<int:user_id>",
        CheckOTPtoChangePassword.as_view(),
        name="verify_password_verify_otp",
    ),
    path(
        "auth/forget-password/confirm/<int:user_id>",
        ConfirmForgetPassword.as_view(),
        name="confirm_forget_password",
    ),
    # ________________________________ User end points _________________________________#
    path(
        "patient/<int:pk>",
        PatientDetailsView.as_view(),
        name="patient_details",
    ),
    path(
        "nurse/<int:pk>",
        NurseDetailsView.as_view(),
        name="nurse_details",
    ),
    path(
        "user/profile/<pk>",
        UpdateUserProfileView.as_view(),
        name="update_user_profile",
    ),
    path(
        "patient/profile/<pk>",
        UpdatePatientProfileView.as_view(),
        name="update_patient_profile",
    ),
    path(
        "nurse/profile/<pk>",
        UpdateNurseProfileView.as_view(),
        name="update_nurse_profile",
    ),
    path(
        "nurse/work_hours/",
        WorkHoursViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="work_hours_list",
    ),
    path(
        "nurse/work_hours/<int:pk>/",
        WorkHoursViewSet.as_view(
            {
                # 'get': 'retrieve',
                "put": "update",
                "delete": "destroy",
            }
        ),
        name="work_hours_detail",
    ),

    
    path("session_type/", SessionTypeListView.as_view(), name="session_type_list"),
    path("session_type/<pk>", SessionTypeRetrieveView.as_view(), name="session_type"),
    path("session_type/craete/", SessionTypeCreateView.as_view(), name="session_type_create"),
    path("session_type/update/<pk>", SessionTypeUpdateView.as_view(), name="session_type_update"),
    path("session_type/delete/<pk>", SessionTypeDeleteView.as_view(), name="session_type_delete"),

    
    path("session_package/", SessionPackageListView.as_view(), name="session_package_list"),
    path("session_package/<pk>", SessionPackageRetrieveView.as_view(), name="session_package"),
    path("session_package/craete/", SessionPackageCreateView.as_view(), name="session_package_create"),
    path("session_package/update/<pk>", SessionPackageUpdateView.as_view(), name="session_package_update"),
    path("session_package/delete/<pk>", SessionPackageDeleteView.as_view(), name="session_package_delete"),

    
    path("session/", SessionListView.as_view(), name="session_list"),
    path("session/<pk>", SessionRetrieveView.as_view(), name="session"),
    path("session/craete/", SessionCreateView.as_view(), name="session_create"),
    path("session/update/<pk>", SessionUpdateView.as_view(), name="session_update"),
    path("session/delete/<pk>", SessionDeleteView.as_view(), name="session_delete"),

    path("session/cancel/<pk>", CancelSessionView.as_view(), name="session_cancel")
]


urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
