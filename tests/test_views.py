import unittest
from unittest.mock import patch

import pandas as pd

from src.views import create_json_response, events_page, main_page


class TestMainPage(unittest.TestCase):

    @patch("src.views.load_transactions")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_main_page_valid_date(self, mock_get_stock_prices, mock_get_currency_rates, mock_load_transactions):
        # Настройка мока для загрузки транзакций
        test_date = "2020-05-01 12:00:00"
        mock_load_transactions.return_value = pd.DataFrame(
            {
                "date": pd.to_datetime(["2020-05-01 12:01:00", "2020-05-01 12:02:00"]),
                "amount": [-10, -20],
                "category": ["Transport", "Food"],
                "description": ["Taxi", "Lunch"],
                "card": ["1234 5678 9876 5432", "1234 5678 9876 5432"],
            }
        )

        # Настройка мока для валютных курсов и цен на акции
        mock_get_currency_rates.return_value = {"USD": 75, "EUR": 90}
        mock_get_stock_prices.return_value = {"AAPL": 150, "GOOGL": 2800}

        # Вызов функции
        response = main_page(test_date, stock_symbol="AAPL")

        # Проверка содержимого ответа
        expected_response = {
            "greeting": "Добрый день",  # Исправьте в зависимости от вашей функции get_greeting()
            "cards": [{"last_digits": "5432", "total_spent": round(-30, 2), "cashback": round(-30 * 0.01, 2)}],
            "top_transactions": [
                {"date": "01.05.2020", "amount": -10, "category": "Transport", "description": "Taxi"},
                {"date": "01.05.2020", "amount": -20, "category": "Food", "description": "Lunch"},
            ],
            "currency_rates": {"USD": 75, "EUR": 90},
            "stock_prices": {"AAPL": 150, "GOOGL": 2800},
        }

        # Сравнение JSON-ответа
        self.assertEqual(response, create_json_response(expected_response))

    def test_main_page_invalid_date_format(self):
        # Вызов функции с неверным форматом даты
        invalid_date = "01-05-2020"
        response = main_page(invalid_date)

        # Проверка на наличие ошибки в ответе
        self.assertEqual(response, '{"error": "Неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS."}')

    @patch("src.views.load_transactions")
    def test_main_page_no_data(self, mock_load_transactions):
        # Настройка мока для загрузки транзакций
        mock_load_transactions.return_value = pd.DataFrame()  # Возвращаем пустой DataFrame

        # Вызов функции с валидной датой
        response = main_page("2020-05-01")

        # Проверка на наличие ошибки в ответе
        self.assertEqual(response, '{"error": "Данные транзакций отсутствуют."}')


class TestEventsPage(unittest.TestCase):

    @patch("src.views.load_transactions")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    def test_events_page_valid_date(self, mock_get_stock_prices, mock_get_currency_rates, mock_load_transactions):
        # Настройка мока для загрузки транзакций
        mock_load_transactions.return_value = pd.DataFrame(
            {
                "date": pd.to_datetime(["2020-05-01 12:00:00", "2020-05-02 12:00:00"]),
                "amount": [-20, 50],
                "category": ["Food", "Salary"],
            }
        )

        mock_get_currency_rates.return_value = {"USD": 75, "EUR": 90}
        mock_get_stock_prices.return_value = {"AAPL": 150, "GOOGL": 2800}

        # Вызов функции с валидной датой
        response = events_page("2020-05-01 12:00:00")

        # Ожидаемый ответ
        expected_response = {
            "expenses": {"total_amount": float(-20), "main": [{"category": "Food", "amount": 20.0}]},
            "income": {"total_amount": float(0), "main": []},  # Убедитесь, что доход не учитывается заэто время
            "currency_rates": {"USD": 75, "EUR": 90},
            "stock_prices": {"AAPL": 150, "GOOGL": 2800},
        }

        # Сравнение JSON-ответа
        self.assertEqual(response, create_json_response(expected_response))

    def test_events_page_invalid_date_format(self):
        # Вызов функции с неверным форматом даты
        invalid_date = "01-05-2020"
        response = events_page(invalid_date)

        # Проверка на наличие ошибки в ответе
        self.assertEqual(
            response, create_json_response({"error": "Неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS."})
        )

    @patch("src.views.load_transactions")
    def test_events_page_no_data(self, mock_load_transactions):
        # Настройка мока для загрузки транзакций (возвращаем пустой DataFrame)
        mock_load_transactions.return_value = pd.DataFrame(columns=["date", "amount", "category"])

        # Вызов функции с валидной датой
        response = events_page("2020-05-01 12:00:00")

        # Проверка на наличие ошибки в ответе
        self.assertEqual(response, create_json_response({"error": "Данные транзакций отсутствуют."}))

    @patch("src.views.load_transactions")
    def test_events_page_no_data_in_period(self, mock_load_transactions):
        # Настройка мока для загрузки транзакций
        mock_load_transactions.return_value = pd.DataFrame(
            {"date": pd.to_datetime(["2020-05-01 12:00:00"]), "amount": [100], "category": ["Salary"]}
        )

        # Вызов функции с валидной датой и заданным периодом (например, 2020-06)
        response = events_page("2020-06-01 12:00:00", period="M")

        # Проверка на наличие ошибки в ответе
        self.assertEqual(response, create_json_response({"error": "Нет данных за указанный период."}))


if __name__ == "__main__":
    unittest.main()
