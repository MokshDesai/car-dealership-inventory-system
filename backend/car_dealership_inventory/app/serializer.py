from rest_framework import serializers

from .models import vehicles


class vehiclesSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=0)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = vehicles
        fields = '__all__'