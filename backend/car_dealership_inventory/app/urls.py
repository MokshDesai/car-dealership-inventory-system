from django.urls import path

from .views import vehiclesManagementView

urlpatterns = [
    path("vehicles/", vehiclesManagementView.as_view()),
    path("vehicles/<int:pk>/", vehiclesManagementView.as_view()),
]
