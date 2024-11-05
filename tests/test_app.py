import logging
import unittest
from unittest import mock

from src.app import app

logging.basicConfig(level=logging.DEBUG)


class FinancialApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Создаем приложение Flask и тестовый клиент один раз для всех тестов."""
        cls.app = app.test_client()
        cls.app.testing = True

    def setUp(self):
        """Вызывается перед каждым тестом, можно использовать для настройки."""
        # Это может включать дополнительные настройки, если необходимо

    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode("utf-8"), "Welcome to the Financial API!")

    @mock.patch("src.views.get_currency_data")
    def test_currency(self, mock_get_currency_data):
        mock_get_currency_data.return_value = [{"currency": "EUR", "rate": 1}, {"currency": "USD", "rate": 1.077348}]

        response = self.app.get("/currency")
        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(len(response_data), 2)
        self.assertIn({"currency": "EUR", "rate": 1}, response_data)

    @mock.patch("src.views.get_stock_data")
    def test_get_stock(self, mock_get_stock_data):
        mock_get_stock_data.return_value = None

        symbol = "MSFT"
        response = self.app.get(f"/stock/{symbol}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"price": 408.46, "stock": "MSFT"}])

    @mock.patch("src.views.get_stock_data")
    def test_get_stock_not_found(self, mock_get_stock_data):
        mock_get_stock_data.side_effect = ValueError("Stock not found")

        symbol = "INVALID"
        response = self.app.get(f"/stock/{symbol}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Stock not found"})

    @mock.patch("src.views.get_currency_data")
    @mock.patch("src.views.get_stock_data")
    def test_get_data_success(self, mock_get_stock_data, mock_get_currency_data):
        mock_get_currency_data.return_value = [{"currency": "EUR", "rate": 1}]
        mock_get_stock_data.side_effect = lambda symbol: {"symbol": symbol, "price": 150.0, "date": "2024-10-28"}

        response = self.app.get("/api/data?date_time=2023-10-01 12:00:00")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("greeting", data)
        self.assertIn("cards", data)
        self.assertIn("top_transactions", data)
        self.assertIn("currency_rates", data)
        self.assertIn("stock_prices", data)

    def test_get_data_missing_date_time(self):
        response = self.app.get("/api/data")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Date and time string is required"})

    def test_get_data_invalid_date_format(self):
        response = self.app.get("/api/data?date_time=invalid_date")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'"})


if __name__ == "__main__":
    unittest.main()
