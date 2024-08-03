"""
URL configuration for Graston project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from django.conf.urls.static import static
from Graston.settings import STATIC_ROOT, STATIC_URL

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from users.views import *

urlpatterns = [
    # admin end point
    path("admin/", admin.site.urls),
    # API auto documentation end points
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
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
    # # User authentication end points
    path("auth/register/", RegisterView.as_view({"post": "create"})),
    path("auth/login/", LoginView.as_view({"post": "login"})),
    path("auth/logout/", LogoutView.as_view({"post": "logout"})),
    path("auth/refresh-token/", RefreshTokenView.as_view({"post": "refresh_token"})),
    path("auth/send-otp2email/<int:user_id>/", VerifyAccount.as_view({"get": "send_otp2email"})),
    path("auth/verify-otp/<int:user_id>/", VerifyAccount.as_view({"post": "verify_otp"})),
    path("auth/user/", UserView.as_view({"get": "retrieve"})),
    # # User end points
    # path("users/", UserViewSet.as_view({"get": "list"})),
    # path(
    #     "users/<int:pk>/",
    #     UserViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    # ),
    # path("users/search/<str:string>/", UserSearch.as_view({"get": "list"})),

    path("auth/delete_account/<pk>", SoftDeleteAccountView.as_view(), name="delete_account"),
    path("auth/reactivate_account/<pk>", RectivateAccountView.as_view(), name="reactivate_account"),

    path("auth/patient/<pk>", PatientDetailsView.as_view(), name="patient_details"),
    path("auth/nurse/<pk>", NurseDetailsView.as_view(), name="nurse_details"),

    path("auth/change_password", PasswordChangeView.as_view(), name="change_password"),
    path("auth/check_password", CheckPasswordView.as_view(), name="check_password"),
]

urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
