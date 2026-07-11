
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import vehicles


def create_vehicle(make, model, category, price, quantity):
    """Helper to create a vehicle quickly in tests."""
    return vehicles.objects.create(
        make=make,
        model=model,
        category=category,
        price=Decimal(str(price)),
        quantity=quantity,
    )


class GetVehiclesListAPITests(APITestCase):
    """
    Tests for: GET /api/vehicles/
    Goal: return all vehicles in inventory (protected endpoint).
    Search filters use the same URL with query params.
    """

    url = "/api/vehicles/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.token = Token.objects.create(user=self.user)

        self.toyota = create_vehicle("Toyota", "Camry", "sedan", "25000.00", 5)
        self.honda = create_vehicle("Honda", "Civic", "sedan", "22000.00", 0)

    # ------------------------------------------------------------------
    # 1. AUTHENTICATION - endpoint must be protected
    # ------------------------------------------------------------------

    def test_returns_401_when_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_401_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token this-is-not-valid")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_200_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # 2. SUCCESS RESPONSE - shape and content
    # ------------------------------------------------------------------

    def test_returns_json_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIsInstance(response.data, list)

    def test_returns_empty_list_when_no_vehicles_exist(self):
        vehicles.objects.all().delete()
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_returns_all_vehicles_in_inventory(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 2)

    def test_each_vehicle_has_required_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        required_fields = {"id", "make", "model", "category", "price", "quantity"}
        for vehicle_data in response.data:
            self.assertEqual(set(vehicle_data.keys()), required_fields)

    def test_vehicle_values_are_correct(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        toyota_data = next(item for item in response.data if item["make"] == "Toyota")

        self.assertEqual(toyota_data["id"], self.toyota.id)
        self.assertEqual(toyota_data["model"], "Camry")
        self.assertEqual(toyota_data["category"], "sedan")
        self.assertEqual(Decimal(str(toyota_data["price"])), Decimal("25000.00"))
        self.assertEqual(toyota_data["quantity"], 5)

    def test_includes_vehicles_with_zero_quantity(self):
        """Out-of-stock vehicles should still appear in the list."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        honda_data = next(item for item in response.data if item["make"] == "Honda")
        self.assertEqual(honda_data["quantity"], 0)


class SearchVehiclesAPITests(APITestCase):
    """
    Tests for: GET /api/vehicles?make=...&model=...
    Goal: filter vehicles by make, model, category, or price range.
    """

    url = "/api/vehicles/"

    def setUp(self):
        self.user = User.objects.create_user(
            username="searchuser",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

        create_vehicle("Toyota", "Camry", "sedan", "25000.00", 5)
        create_vehicle("Honda", "Civic", "sedan", "22000.00", 3)
        create_vehicle("Ford", "F-150", "truck", "45000.00", 2)
        create_vehicle("Tesla", "Model 3", "electric", "42000.00", 1)

    # ------------------------------------------------------------------
    # 1. AUTHENTICATION
    # ------------------------------------------------------------------

    def test_search_returns_401_when_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------
    # 2. SEARCH BY MAKE
    # ------------------------------------------------------------------

    def test_search_by_make_returns_matching_vehicles(self):
        response = self.client.get(self.url, {"make": "Toyota"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["make"], "Toyota")

    def test_search_by_make_is_case_insensitive(self):
        response = self.client.get(self.url, {"make": "toyota"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_by_make_with_no_match_returns_empty_list(self):
        response = self.client.get(self.url, {"make": "BMW"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # ------------------------------------------------------------------
    # 3. SEARCH BY MODEL
    # ------------------------------------------------------------------

    def test_search_by_model_returns_matching_vehicles(self):
        response = self.client.get(self.url, {"model": "Civic"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["model"], "Civic")

    # ------------------------------------------------------------------
    # 4. SEARCH BY CATEGORY
    # ------------------------------------------------------------------

    def test_search_by_category_returns_matching_vehicles(self):
        response = self.client.get(self.url, {"category": "sedan"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_by_category_truck(self):
        response = self.client.get(self.url, {"category": "truck"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["make"], "Ford")

    # ------------------------------------------------------------------
    # 5. SEARCH BY PRICE RANGE
    # ------------------------------------------------------------------

    def test_search_by_min_price(self):
        response = self.client.get(self.url, {"min_price": "40000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_by_max_price(self):
        response = self.client.get(self.url, {"max_price": "23000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["make"], "Honda")

    def test_search_by_price_range(self):
        response = self.client.get(
            self.url,
            {"min_price": "22000", "max_price": "26000"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    # ------------------------------------------------------------------
    # 6. COMBINED FILTERS & NO FILTERS
    # ------------------------------------------------------------------

    def test_search_with_multiple_filters(self):
        response = self.client.get(
            self.url,
            {"make": "Toyota", "category": "sedan", "max_price": "30000"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["model"], "Camry")

    def test_search_without_filters_returns_all_vehicles(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
