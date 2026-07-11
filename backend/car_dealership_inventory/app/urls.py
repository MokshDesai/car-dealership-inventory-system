from django.urls import path

from .views import (
    auth_login,
    auth_logout,
    auth_register,
    purchase_vehicle,
    vehiclesManagementView,
    vehiclesRestockView,
)

urlpatterns = [
    path("auth/register/", auth_register),
    path("auth/login/", auth_login),
    path("auth/logout/", auth_logout),
    path("vehicles/", vehiclesManagementView.as_view()),
    path("vehicles/<int:pk>/", vehiclesManagementView.as_view()),
    path("vehicles/<int:pk>/purchase/", purchase_vehicle),
    path("vehicles/<int:pk>/restock/", vehiclesRestockView),
]
