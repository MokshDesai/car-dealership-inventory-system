from django.contrib import admin
from .models import vehicles

@admin.register(vehicles)
class VehiclesAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'category', 'price', 'quantity')