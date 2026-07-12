from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import vehicles
from .serializer import vehiclesSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'user')

    if role == 'admin':
        return Response(
            {'error': 'Admin accounts cannot be created via API.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if role != 'user':
        return Response({'error': 'Role must be user.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not username or not email or not password:
        return Response({'error': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Basic verification
    if '@' not in email or '.' not in email:
        return Response({'error': 'Please enter a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            'message': 'User registered successfully.',
            'token': token.key,
            'username': user.username,
            'role': 'user',
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials.'}, status=400)

    token, _ = Token.objects.get_or_create(user=user)
    login(request, user)
    role = 'admin' if user.is_staff else 'user'
    return Response({'message': 'Login successful.', 'token': token.key, 'role': role})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    if request.auth:
        request.auth.delete()
    logout(request)
    return Response({'message': 'Logout successful.'})
    


class vehiclesManagementView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return [IsAuthenticated()]

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

    def post(self, request):
        serializer = vehiclesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            vehicle = vehicles.objects.get(pk=pk)
        except vehicles.DoesNotExist:
            return Response({"error": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = vehiclesSerializer(vehicle, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            vehicle = vehicles.objects.get(pk=pk)
        except vehicles.DoesNotExist:
            return Response({"error": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND)

        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def purchase_vehicle(request, pk):
    try:
        vehicle = vehicles.objects.get(pk=pk)
    except vehicles.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if vehicle.quantity <= 0:
        return Response({"error": "Out of stock"}, status=status.HTTP_400_BAD_REQUEST)

    vehicle.quantity -= 1
    vehicle.save()
    serializer = vehiclesSerializer(vehicle)
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def vehiclesRestockView(request, pk):
    try:
        vehicle = vehicles.objects.get(pk=pk)
    except vehicles.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    vehicle.quantity += 1
    vehicle.save()
    serializer = vehiclesSerializer(vehicle)
    return Response(serializer.data, status=status.HTTP_200_OK)
