from django.urls import path

from .views import vehiclesDetailView, vehiclesListView

urlpatterns = [
    path("vehicles/", vehiclesListView.as_view()),
    path("vehicles/<int:pk>/", vehiclesDetailView.as_view()),
]
