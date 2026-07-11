from django.urls import path

from .views import vehiclesListView, vehiclesSearchView

urlpatterns = [
    path("vehicles/search/", vehiclesSearchView.as_view()),
    path("vehicles/", vehiclesListView.as_view()),
]
