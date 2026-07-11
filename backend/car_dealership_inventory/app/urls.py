from django.urls import path

from .views import vehiclesManagementView, vehiclesPurchaseView, vehiclesRestockView

urlpatterns = [
    path("vehicles/", vehiclesManagementView.as_view()),
    path("vehicles/<int:pk>/", vehiclesManagementView.as_view()),
    path("vehicles/<int:pk>/purchase/", vehiclesPurchaseView.as_view()),
    path("vehicles/<int:pk>/restock/", vehiclesRestockView.as_view()),
]
