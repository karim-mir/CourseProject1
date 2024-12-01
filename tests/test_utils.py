import json
import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from src.utils import calculate_cashback, get_currency_rates, get_greeting, get_stock_prices, load_user_settings


class TestUtils(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"setting1": "value1"}))
    def test_load_user_settings(self, mock_file):
        settings = load_user_settings("dummy_path")
        self.assertEqual(settings, {"setting1": "value1"})
        mock_file.assert_called_once_with("dummy_path", "r")

    @patch("src.utils.datetime")
    def test_get_greeting_morning(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 1, 1, 9)  # 9 AM
        self.assertEqual(get_greeting(), "Доброе утро")

    @patch("src.utils.datetime")
    def test_get_greeting_afternoon(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 1, 1, 15)  # 3 PM
        self.assertEqual(get_greeting(), "Добрый день")

    @patch("src.utils.datetime")
    def test_get_greeting_evening(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2023, 1, 1, 19)  # 7 PM
        self.assertEqual(get_greeting(), "Добрый вечер")

    @patch("src.utils.requests.get")
    def test_get_currency_rates_success(self, mock_requests_get):
        # Mocking the response from requests.get
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"rates": {"USD": 74.5, "EUR": 88.2}, "success": True}

        user_currencies = ["USD", "EUR"]
        rates = get_currency_rates(user_currencies)

        expected_rates = [{"currency": "USD", "rate": 74.5}, {"currency": "EUR", "rate": 88.2}]
        self.assertEqual(rates, expected_rates)

    @patch("src.utils.requests.get")
    def test_get_currency_rates_failure(self, mock_requests_get):
        # Mocking the response with an error
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 400  # Bad request
        mock_response.text = "Bad Request"

        user_currencies = ["USD"]
        rates = get_currency_rates(user_currencies)

        self.assertEqual(rates, [])  # Should return empty on failure

    @patch("src.utils.requests.get")
    def test_get_stock_prices_success(self, mock_requests_get):
        # Создание фальшивого ответа для успешного запроса
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Time Series (1min)": {
                "2023-01-01 15:00:00": {"1. open": "150.00"},
                "2023-01-01 15:01:00": {"1. open": "151.00"},
            }
        }

        user_stocks = ["AAPL", "MSFT"]
        prices = get_stock_prices(user_stocks)

        expected_prices = [
            {"stock": "AAPL", "price": 150.00},
            {"stock": "MSFT", "price": 150.00},  # Последняя цена для MSFT также будет охвачена
        ]

        self.assertEqual(prices, expected_prices)

    @patch("src.utils.requests.get")
    def test_get_stock_prices_no_data(self, mock_requests_get):
        # Создание фальшивого ответа без данных Time Series
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"Error Message": "Invalid API call"}

        user_stocks = ["AAPL"]
        prices = get_stock_prices(user_stocks)

        self.assertEqual(prices, [])  # Должно вернуть пустой список

    @patch("src.utils.requests.get")
    def test_get_stock_prices_api_error(self, mock_requests_get):
        # Создание фальшивого ответа с ошибкой
        mock_response = mock_requests_get.return_value
        mock_response.status_code = 400  # Bad request

        user_stocks = ["AAPL"]
        prices = get_stock_prices(user_stocks)

        self.assertEqual(prices, [])  # Должно вернуть пустой список

    def test_calculate_cashback(self):
        total_spent = 100.00
        cashback = calculate_cashback(total_spent)

        self.assertEqual(cashback, 1.00)  # 1% от 100.00 должно быть 1.00


if __name__ == "__main__":
    unittest.main()
