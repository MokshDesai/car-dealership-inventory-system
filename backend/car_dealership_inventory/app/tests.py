
from decimal import Decimal

from rest_framework import status
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
    Goal: return all vehicles in inventory (public endpoint for now).
    Search filters use the same URL with query params.
    """

    url = "/api/vehicles/"

    def setUp(self):
        self.toyota = create_vehicle("Toyota", "Camry", "sedan", "25000.00", 5)
        self.honda = create_vehicle("Honda", "Civic", "sedan", "22000.00", 0)

    def test_returns_200_without_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_json_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIsInstance(response.data, list)

    def test_returns_empty_list_when_no_vehicles_exist(self):
        vehicles.objects.all().delete()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_returns_all_vehicles_in_inventory(self):
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 2)

    def test_each_vehicle_has_required_fields(self):
        response = self.client.get(self.url)

        required_fields = {"id", "make", "model", "category", "price", "quantity"}
        for vehicle_data in response.data:
            self.assertEqual(set(vehicle_data.keys()), required_fields)

    def test_vehicle_values_are_correct(self):
        response = self.client.get(self.url)

        toyota_data = next(item for item in response.data if item["make"] == "Toyota")

        self.assertEqual(toyota_data["id"], self.toyota.id)
        self.assertEqual(toyota_data["model"], "Camry")
        self.assertEqual(toyota_data["category"], "sedan")
        self.assertEqual(Decimal(str(toyota_data["price"])), Decimal("25000.00"))
        self.assertEqual(toyota_data["quantity"], 5)

    def test_includes_vehicles_with_zero_quantity(self):
        """Out-of-stock vehicles should still appear in the list."""
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
        create_vehicle("Toyota", "Camry", "sedan", "25000.00", 5)
        create_vehicle("Honda", "Civic", "sedan", "22000.00", 3)
        create_vehicle("Ford", "F-150", "truck", "45000.00", 2)
        create_vehicle("Tesla", "Model 3", "electric", "42000.00", 1)

    # ------------------------------------------------------------------
    # 1. SEARCH BY MAKE
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


class PostVehiclesAPITests(APITestCase):
    """
    Tests for: POST /api/vehicles/
    Goal: add a new vehicle to inventory.
    """

    url = "/api/vehicles/"

    def valid_payload(self):
        return {
            "make": "BMW",
            "model": "X5",
            "category": "suv",
            "price": "55000.00",
            "quantity": 3,
        }

    # ------------------------------------------------------------------
    # 1. SUCCESS
    # ------------------------------------------------------------------

    def test_creates_vehicle_with_valid_data(self):
        response = self.client.post(self.url, self.valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_returns_created_vehicle_with_all_fields(self):
        response = self.client.post(self.url, self.valid_payload(), format="json")

        required_fields = {"id", "make", "model", "category", "price", "quantity"}
        self.assertEqual(set(response.data.keys()), required_fields)
        self.assertEqual(response.data["make"], "BMW")
        self.assertEqual(response.data["model"], "X5")
        self.assertEqual(response.data["category"], "suv")
        self.assertEqual(Decimal(str(response.data["price"])), Decimal("55000.00"))
        self.assertEqual(response.data["quantity"], 3)

    def test_saves_vehicle_to_database(self):
        response = self.client.post(self.url, self.valid_payload(), format="json")

        self.assertTrue(vehicles.objects.filter(id=response.data["id"]).exists())
        self.assertEqual(vehicles.objects.count(), 1)

    def test_auto_generates_unique_id(self):
        first = self.client.post(self.url, self.valid_payload(), format="json")
        second = self.client.post(
            self.url,
            {**self.valid_payload(), "make": "Audi", "model": "Q7"},
            format="json",
        )

        self.assertNotEqual(first.data["id"], second.data["id"])

    def test_allows_zero_quantity(self):
        payload = {**self.valid_payload(), "quantity": 0}
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 0)

    # ------------------------------------------------------------------
    # 2. VALIDATION ERRORS
    # ------------------------------------------------------------------

    def test_returns_400_when_make_is_missing(self):
        payload = self.valid_payload()
        del payload["make"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("make", response.data)

    def test_returns_400_when_model_is_missing(self):
        payload = self.valid_payload()
        del payload["model"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("model", response.data)

    def test_returns_400_when_category_is_missing(self):
        payload = self.valid_payload()
        del payload["category"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)

    def test_returns_400_when_price_is_missing(self):
        payload = self.valid_payload()
        del payload["price"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_returns_400_when_quantity_is_missing(self):
        payload = self.valid_payload()
        del payload["quantity"]
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_returns_400_when_quantity_is_negative(self):
        payload = {**self.valid_payload(), "quantity": -1}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_returns_400_when_price_is_negative(self):
        payload = {**self.valid_payload(), "price": "-100.00"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_returns_400_when_price_is_not_a_number(self):
        payload = {**self.valid_payload(), "price": "not-a-price"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_returns_400_when_body_is_empty(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PutVehiclesAPITests(APITestCase):
    """
    Tests for: PUT /api/vehicles/:id/
    Goal: update a vehicle's details.
    """

    def setUp(self):
        self.vehicle = create_vehicle("Toyota", "Camry", "sedan", "25000.00", 5)
        self.url = f"/api/vehicles/{self.vehicle.id}/"

    def valid_payload(self):
        return {
            "make": "Toyota",
            "model": "Camry Hybrid",
            "category": "hybrid",
            "price": "28000.00",
            "quantity": 8,
        }

    # ------------------------------------------------------------------
    # 1. SUCCESS
    # ------------------------------------------------------------------

    def test_updates_vehicle_with_valid_data(self):
        response = self.client.put(self.url, self.valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_updated_vehicle_with_all_fields(self):
        response = self.client.put(self.url, self.valid_payload(), format="json")

        required_fields = {"id", "make", "model", "category", "price", "quantity"}
        self.assertEqual(set(response.data.keys()), required_fields)
        self.assertEqual(response.data["id"], self.vehicle.id)
        self.assertEqual(response.data["model"], "Camry Hybrid")
        self.assertEqual(response.data["category"], "hybrid")
        self.assertEqual(Decimal(str(response.data["price"])), Decimal("28000.00"))
        self.assertEqual(response.data["quantity"], 8)

    def test_persists_changes_to_database(self):
        self.client.put(self.url, self.valid_payload(), format="json")

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.model, "Camry Hybrid")
        self.assertEqual(self.vehicle.category, "hybrid")
        self.assertEqual(self.vehicle.price, Decimal("28000.00"))
        self.assertEqual(self.vehicle.quantity, 8)

    def test_does_not_change_vehicle_id(self):
        original_id = self.vehicle.id
        self.client.put(self.url, self.valid_payload(), format="json")

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.id, original_id)

    def test_does_not_affect_other_vehicles(self):
        other = create_vehicle("Honda", "Civic", "sedan", "22000.00", 3)
        self.client.put(self.url, self.valid_payload(), format="json")

        other.refresh_from_db()
        self.assertEqual(other.model, "Civic")
        self.assertEqual(other.quantity, 3)

    def test_allows_zero_quantity(self):
        payload = {**self.valid_payload(), "quantity": 0}
        response = self.client.put(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 0)

    # ------------------------------------------------------------------
    # 2. NOT FOUND
    # ------------------------------------------------------------------

    def test_returns_404_when_vehicle_does_not_exist(self):
        url = f"/api/vehicles/99999/"
        response = self.client.put(url, self.valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------
    # 3. VALIDATION ERRORS
    # ------------------------------------------------------------------

    def test_returns_400_when_make_is_missing(self):
        payload = self.valid_payload()
        del payload["make"]
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("make", response.data)

    def test_returns_400_when_model_is_missing(self):
        payload = self.valid_payload()
        del payload["model"]
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("model", response.data)

    def test_returns_400_when_category_is_missing(self):
        payload = self.valid_payload()
        del payload["category"]
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)

    def test_returns_400_when_price_is_missing(self):
        payload = self.valid_payload()
        del payload["price"]
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_returns_400_when_quantity_is_missing(self):
        payload = self.valid_payload()
        del payload["quantity"]
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_returns_400_when_quantity_is_negative(self):
        payload = {**self.valid_payload(), "quantity": -1}
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)

    def test_returns_400_when_price_is_negative(self):
        payload = {**self.valid_payload(), "price": "-100.00"}
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_returns_400_when_price_is_not_a_number(self):
        payload = {**self.valid_payload(), "price": "not-a-price"}
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)

    def test_returns_400_when_body_is_empty(self):
        response = self.client.put(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteVehiclesAPITests(APITestCase):
    """
    Tests for: DELETE /api/vehicles/:id/
    Goal: delete a vehicle from inventory.
    """

    list_url = "/api/vehicles/"

    def setUp(self):
        self.vehicle = create_vehicle("Toyota", "Camry", "sedan", "25000.00", 5)
        self.url = f"/api/vehicles/{self.vehicle.id}/"

    # ------------------------------------------------------------------
    # 1. SUCCESS
    # ------------------------------------------------------------------

    def test_deletes_vehicle_successfully(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_removes_vehicle_from_database(self):
        self.client.delete(self.url)
        self.assertFalse(vehicles.objects.filter(id=self.vehicle.id).exists())

    def test_does_not_affect_other_vehicles(self):
        other = create_vehicle("Honda", "Civic", "sedan", "22000.00", 3)
        self.client.delete(self.url)

        self.assertFalse(vehicles.objects.filter(id=self.vehicle.id).exists())
        self.assertTrue(vehicles.objects.filter(id=other.id).exists())

    def test_deleted_vehicle_not_in_list(self):
        self.client.delete(self.url)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    # ------------------------------------------------------------------
    # 2. NOT FOUND
    # ------------------------------------------------------------------

    def test_returns_404_when_vehicle_does_not_exist(self):
        url = "/api/vehicles/99999/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
