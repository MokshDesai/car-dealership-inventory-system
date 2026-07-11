from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import vehicles
from .serializer import vehiclesSerializer


class vehiclesListView(APIView):
    def get(self, request):
        queryset = vehicles.objects.all()

        make = request.query_params.get("make")
        model = request.query_params.get("model")
        category = request.query_params.get("category")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if make:
            queryset = queryset.filter(make__iexact=make)
        if model:
            queryset = queryset.filter(model__iexact=model)
        if category:
            queryset = queryset.filter(category__iexact=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        serializer = vehiclesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
