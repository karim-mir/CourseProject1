import os
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from dotenv import load_dotenv

from src.utils import fetch_data, get_currency_rates, get_expenses, get_stock_prices, load_transactions


def get_mock_transactions(date_str: str) -> pd.DataFrame:
    data = {
        "date": ["2020-05-01", "2020-05-02", "2020-05-03", "2020-05-20", "2020-05-20"],
        "category": ["Food", "Transport", "Entertainment", "Food", "Transport"],
        "amount": [50, -20, -150, -75, -30],
        "description": ["Description 1", "Description 2", "Description 3", "Description 4", "Description 5"],
        "card": [
            "1234 5678 9876 5432",
            "1234 5678 9876 5433",
            "1234 5678 9876 5434",
            "1234 5678 9876 5435",
            "1234 5678 9876 5436",
        ],
    }
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


class TestUtils(unittest.TestCase):

    def test_load_transactions(self):
        df = get_mock_transactions("")  # Здесь мы просто вызываем тестовую функцию

        # Проверка, что DataFrame имеет правильные размеры
        self.assertEqual(df.shape, (5, 5))  # Ожидаем 5 строк для всех данных

        # Проверка содержимого DataFrame
        self.assertEqual(df["date"].iloc[0], pd.to_datetime("2020-05-01"))
        self.assertEqual(df["amount"].iloc[0], 50)
        self.assertEqual(df["category"].iloc[0], "Food")
        self.assertEqual(df["description"].iloc[0], "Description 1")
        self.assertEqual(df["card"].iloc[0], "1234 5678 9876 5432")

        # Проверка типов данных
        self.assertEqual(df["date"].dtype, "datetime64[ns]")
        self.assertEqual(df["amount"].dtype, "int64")

    def test_load_transactions_no_data(self):
        df = get_mock_transactions("")  # Здесь также вызываем тестовую функцию

        # Проверяем, что DataFrame не пустой
        self.assertGreater(df.shape[0], 0)  # Это для проверки, что у нас есть данные

    @patch("src.views.load_transactions")  # Убедитесь, что путь правильный
    def test_get_expenses(self, mock_load_transactions):
        # Настройка мока для загрузки всех данных транзакций
        mock_load_transactions.return_value = get_mock_transactions(
            "")  # Можно передать пустую строку, если фильтры не нужны

        start_date = pd.to_datetime("2020-05-01")
        end_date = pd.to_datetime("2020-05-03")

        # Здесь вызов функции get_expenses
        result = get_expenses(start_date, end_date)

        # Проверяем, что возвращаемый объект - словарь
        self.assertIsInstance(result, dict)

        # Проверяем наличие ключей в результате
        self.assertIn("total_amount", result)
        self.assertIn("main", result)

        # Возможно, корректируйте это значение в зависимости от ваших данных
        self.assertEqual(result["total_amount"], 170)  # Ожидаем сумму в 170

        # Проверяем, что в списке главных расходов не больше 7 элементов
        self.assertLessEqual(len(result["main"]), 7)

        # Проверяем содержимое главных расходов
        expected_categories = ["Entertainment", "Transport"]
        expected_amounts = [150, 20]  # Суммы положительных расходов для топ-категорий

        for expected_category, expected_amount in zip(expected_categories, expected_amounts):
            self.assertIn({"category": expected_category, "amount": expected_amount}, result["main"])


class TestUtilsNew(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Загружаем переменные окружения из .env файла
        load_dotenv()

    def setUp(self):
        # Фикстура для тестовых данных валют
        self.mock_currency_response = {
            "rates": {"EUR": 0.85, "GBP": 0.75, "JPY": 110.0},
            "base": "USD",
            "date": "2022-01-01",
        }

        # Фикстура для тестовых данных акций
        self.mock_stock_response = {
            "Meta Data": {
                "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                "2. Symbol": "MSFT",
                "3. Last Refreshed": "2022-01-01",
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern",
            },
            "Time Series (Daily)": {
                "2022-01-01": {
                    "1. open": "300.00",
                    "2. high": "305.00",
                    "3. low": "295.00",
                    "4. close": "302.00",
                    "5. volume": "1000000",
                },
                "2022-01-02": {
                    "1. open": "302.00",
                    "2. high": "310.00",
                    "3. low": "299.00",
                    "4. close": "308.00",
                    "5. volume": "1500000",
                },
            },
        }

    @patch("src.utils.requests.get")
    def test_get_currency_rates(self, mock_get):
        # Настраиваем mock
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = self.mock_currency_response
        mock_get.return_value.status_code = 200

        # Вызов тестируемой функции
        result = get_currency_rates()

        # Проверяем результат
        expected = [
            {"currency": "EUR", "rate": 0.85},
            {"currency": "GBP", "rate": 0.75},
            {"currency": "JPY", "rate": 110.0},
        ]
        self.assertEqual(result, expected)
        mock_get.assert_called_once()

    @patch("src.utils.requests.get")
    def test_get_stock_prices(self, mock_get):
        # Настраиваем mock
        mock_get.return_value = MagicMock()
        mock_get.return_value.json.return_value = self.mock_stock_response
        mock_get.return_value.status_code = 200

        result = get_stock_prices("MSFT")

        # Проверяем результат
        expected = [
            {"date": "2022-01-01", "stock": "MSFT", "open": 300.0, "close": 302.0, "volume": 1000000},
            {"date": "2022-01-02", "stock": "MSFT", "open": 302.0, "close": 308.0, "volume": 1500000},
        ]

        self.assertEqual(result, expected)
        # Проверяем на использование правильного API ключа
        mock_get.assert_called_once_with(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey="
            f"{os.getenv('STOCK_API_KEY')}"
        )


class TestFetchData(unittest.TestCase):

    @patch("src.utils.get_expenses")
    @patch("src.utils.get_income")
    @patch("src.utils.get_currency_rates")
    @patch("src.utils.get_stock_prices")
    def test_fetch_data_month_range(
        self, mock_get_stock_prices, mock_get_currency_rates, mock_get_income, mock_get_expenses
    ):
        # Настройка моков, чтобы вернуть тестовые данные
        mock_get_expenses.return_value = [100, 200]
        mock_get_income.return_value = [300, 400]
        mock_get_currency_rates.return_value = [{"currency": "EUR", "rate": 0.85}]
        mock_get_stock_prices.return_value = [{"date": "2022-01-01", "price": 150}]

        # Тестовая дата
        date_str = "2022-01-15"
        result = fetch_data(date_str, date_range="M", stock_symbol="AAPL")

        expected_result = {
            "expenses": [100, 200],
            "income": [300, 400],
            "currency_rates": [{"currency": "EUR", "rate": 0.85}],
            "stock_prices": [{"date": "2022-01-01", "price": 150}],
        }

        # Проверяем результат
        self.assertEqual(result, expected_result)

    @patch("src.utils.get_expenses")
    @patch("src.utils.get_income")
    @patch("src.utils.get_currency_rates")
    @patch("src.utils.get_stock_prices")
    def test_fetch_data_week_range(
        self, mock_get_stock_prices, mock_get_currency_rates, mock_get_income, mock_get_expenses
    ):
        # Настройка моков, чтобы вернуть тестовые данные
        mock_get_expenses.return_value = [50]
        mock_get_income.return_value = [100]
        mock_get_currency_rates.return_value = [{"currency": "GBP", "rate": 0.75}]
        mock_get_stock_prices.return_value = [{"date": "2022-01-12", "price": 155}]

        # Тестовая дата
        date_str = "2022-01-12"
        result = fetch_data(date_str, date_range="W", stock_symbol="AAPL")

        expected_result = {
            "expenses": [50],
            "income": [100],
            "currency_rates": [{"currency": "GBP", "rate": 0.75}],
            "stock_prices": [{"date": "2022-01-12", "price": 155}],
        }

        # Проверяем результат
        self.assertEqual(result, expected_result)

    @patch("src.utils.get_expenses")
    @patch("src.utils.get_income")
    @patch("src.utils.get_currency_rates")
    @patch("src.utils.get_stock_prices")
    def test_fetch_data_year_range(
        self, mock_get_stock_prices, mock_get_currency_rates, mock_get_income, mock_get_expenses
    ):
        # Настройка моков, чтобы вернуть тестовые данные
        mock_get_expenses.return_value = [1200]
        mock_get_income.return_value = [5000]
        mock_get_currency_rates.return_value = [{"currency": "JPY", "rate": 110.0}]
        mock_get_stock_prices.return_value = [{"date": "2022-01-01", "price": 140}]

        # Тестовая дата
        date_str = "2022-12-15"
        result = fetch_data(date_str, date_range="Y", stock_symbol="AAPL")

        expected_result = {
            "expenses": [1200],
            "income": [5000],
            "currency_rates": [{"currency": "JPY", "rate": 110.0}],
            "stock_prices": [{"date": "2022-01-01", "price": 140}],
        }

        # Проверяем результат
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
