from django.urls import path

from .views import vehiclesListView

urlpatterns = [
    path("vehicles/", vehiclesListView.as_view()),
]
