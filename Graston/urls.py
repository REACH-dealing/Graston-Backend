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
    # path("auth/logout/", LogoutView.as_view({"post": "logout"})),
    # path("auth/user/", UserView.as_view({"get": "retrieve"})),
    # # User end points
    # path("users/", UserViewSet.as_view({"get": "list"})),
    # path(
    #     "users/<int:pk>/",
    #     UserViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    # ),
    # path("users/search/<str:string>/", UserSearch.as_view({"get": "list"})),
    path("send-email/", send_simple_email, name="send_email"),
    path("api/token/", Tokens.as_view({"post": "post"}), name="token_obtain_pair"),
]
