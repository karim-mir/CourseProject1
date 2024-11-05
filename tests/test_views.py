import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.views import calculate_expenses, filter_transactions, generate_report, get_currency_data, get_stock_data


class TestFinanceModule(unittest.TestCase):
    """Тесты для модуля финансовых операций."""

    @classmethod
    def setUpClass(cls):
        """Настройка окружения для всех тестов."""
        os.environ["CURRENCY_API_URL"] = "http://fakeapi.com"
        os.environ["CURRENCY_API_KEY"] = "fakeapikey"
        os.environ["STOCK_API_URL"] = "http://fakeapi.com"
        os.environ["STOCK_API_KEY"] = "fakeapikey"

    def setUp(self):
        """Инициализация тестовых данных перед каждым тестом."""
        self.transactions = [
            {"date": "2020-05-01", "amount": -17319, "category": "Супермаркеты"},
            {"date": "2020-05-02", "amount": -3324, "category": "Фастфуд"},
            {"date": "2020-05-03", "amount": -2289, "category": "Топливо"},
            {"date": "2020-05-04", "amount": -1850, "category": "Развлечения"},
            {"date": "2020-05-10", "amount": 33000, "category": "Пополнение_BANK007"},
            {"date": "2020-05-15", "amount": 1242, "category": "Проценты_на_остаток"},
        ]

    @patch("src.views.requests.get")
    def test_get_currency_data(self, mock_get):
        """Тест получения данных о валюте."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"rates": {"USD": 74.21, "EUR": 88.47}}
        mock_get.return_value = mock_response

        results = get_currency_data()
        expected = [{"currency": "USD", "rate": 74.21}, {"currency": "EUR", "rate": 88.47}]
        self.assertEqual(results, expected)

    def test_filter_transactions(self):
        """Тест фильтрации транзакций по дате."""
        start_date = datetime.strptime("2020-05-01", "%Y-%m-%d")
        end_date = datetime.strptime("2020-05-03", "%Y-%m-%d")
        filtered = filter_transactions(start_date, end_date)
        self.assertEqual(len(filtered), 3)  # Должно вернуть 3 транзакции

    def test_calculate_expenses(self):
        """Тест калькуляции расходов."""
        expenses = calculate_expenses(self.transactions)
        self.assertEqual(expenses["total_amount"], 24782)  # Общая сумма расходов
        self.assertEqual(len(expenses["main"]), 5)  # Должно вернуть 5 основные категории

    @patch("src.views.requests.get")
    def test_get_stock_data(self, mock_get):
        """Тест получения данных о фондовом рынке."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"Time Series (Daily)": {"2020-05-15": {"4. close": "100.00"}}}
        mock_response.headers = {"Content-Type": "application/json"}  # Установка заголовка
        mock_response.status_code = 200  # Установка успешного кода ответа
        mock_get.return_value = mock_response  # Возвращаем мок-ответ

        result = get_stock_data("AAPL")
        self.assertEqual(result, [{"stock": "AAPL", "price": 100.00}])

    @patch("src.views.requests.get")
    def test_get_stock_data_invalid_json(self, mock_get):
        """Тест получения данных о фондовом рынке с некорректным JSON."""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/html"}  # Некорректный заголовок
        mock_response.status_code = 200  # Установка успешного кода ответа
        mock_get.return_value = mock_response  # Возвращаем некорректный мок-ответ

        with self.assertRaises(ValueError) as context:
            get_stock_data("AAPL")

        self.assertEqual(
            str(context.exception),
            "Ошибка парсинга JSON: Получена некорректная страница вместо JSON. Проверьте API URL и ключ.",
        )

    @patch("src.views.get_currency_data")
    @patch("src.views.get_stock_data")
    @patch("src.views.filter_transactions")
    @patch("src.views.calculate_expenses")
    def test_generate_report(
        self, mock_calculate_expenses, mock_filter_transactions, mock_get_stock_data, mock_get_currency_data
    ):
        """Тест генерации финансового отчета."""
        mock_filter_transactions.return_value = self.transactions
        mock_calculate_expenses.return_value = {"total_amount": 24782, "main": []}
        mock_get_currency_data.return_value = [{"currency": "USD", "rate": 74.21}]
        mock_get_stock_data.return_value = [{"stock": "AAPL", "price": 100.00}]

        report = generate_report("2020-05-15", "AAPL")

        self.assertIn("expenses", report)
        self.assertIn("currency_rates", report)
        self.assertIn("stock_prices", report)
        self.assertEqual(report["stock_prices"], [{"stock": "AAPL", "price": 100.00}])


if __name__ == "__main__":
    unittest.main()
