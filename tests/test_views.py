import json  # Добавляем импорт json
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.views import create_json_response, generate_report, load_operations_data


class TestJsonResponse(unittest.TestCase):

    def test_create_json_response(self):
        greeting = "Доброе утро"
        cards = [
            {"last_digits": "7197", "total_spent": -2319507.75, "cashback": -23195.08},
            {"last_digits": "5091", "total_spent": -14918.16, "cashback": -149.18},
            {"last_digits": "nan", "total_spent": 530864.3, "cashback": 5308.64},
            {"last_digits": "4556", "total_spent": 545261.72, "cashback": 5452.62},
            {"last_digits": "1112", "total_spent": -46207.08, "cashback": -462.07},
            {"last_digits": "5507", "total_spent": -84000.0, "cashback": -840.0},
            {"last_digits": "6002", "total_spent": -69200.0, "cashback": -692.0},
            {"last_digits": "5441", "total_spent": -470854.8, "cashback": -4708.55},
        ]
        top_transactions = [
            {
                "date": "21.03.2019",
                "amount": 190044.51,
                "category": "Переводы",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR",
            },
            {
                "date": "23.10.2018",
                "amount": 177506.03,
                "category": "Переводы",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR",
            },
            {
                "date": "30.12.2021",
                "amount": 174000.0,
                "category": "Пополнения",
                "description": "Пополнение через Газпромбанк",
            },
            {"date": "14.09.2021", "amount": 150000.0, "category": "Пополнения", "description": "Перевод с карты"},
            {"date": "01.08.2020", "amount": 150000.0, "category": "Пополнения", "description": "Перевод с карты"},
        ]
        currency_rates = []
        stock_prices = [{"stock": "AAPL", "price": 237.36}, {"stock": "AMZN", "price": 208.25}]

        expected_response = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        json_response = create_json_response(greeting, cards, top_transactions, currency_rates, stock_prices)
        result_dict = json.loads(json_response)

        self.assertEqual(result_dict, expected_response)

    def test_create_json_response_empty(self):
        json_response = create_json_response("", [], [], [], [])
        expected_response = {
            "greeting": "",
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": [],
        }
        result_dict = json.loads(json_response)
        self.assertEqual(result_dict, expected_response)

    def test_create_json_response_no_indent(self):
        greeting = "Привет"
        json_response = create_json_response(greeting, [], [], [], [])
        self.assertIn("Привет", json_response)  # Убедимся, что greeting присутствует в ответе

        # Проверяем, что JSON имеет правильный отступ
        json_response_unformatted = json_response.replace("\n", "").replace(" ", "")
        self.assertEqual(
            json_response_unformatted.count(
                '{"greeting":"Привет","cards":[],"top_transactions":[],"currency_rates":[],"stock_prices":[]}'
            ),
            1,
        )


class TestLoadOperationsData(unittest.TestCase):

    @patch("src.views.pd.read_excel")
    def test_load_operations_data_success(self, mock_read_excel):
        mock_df = pd.DataFrame(
            {
                "Номер карты": ["1234567890123456", "9876543210987654"],
                "Сумма операции": [100.0, 200.0],
                "Дата операции": ["01.01.2021 12:00:00", "02.01.2021 14:00:00"],
                "Сумма платежа": [90.0, 180.0],
                "Дата платежа": ["01.01.2021", "02.01.2021"],
            }
        )
        mock_read_excel.return_value = mock_df

        result = load_operations_data("fake_path.xlsx")
        print(result)  # Проверяем, что возвращается

        expected_result = [
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": 100.0,
                "Дата операции": pd.Timestamp("2021-01-01 12:00:00"),  # Оставляем в формате Timestamp
                "Сумма платежа": 90.0,
                "Дата платежа": pd.Timestamp("2021-01-01"),  # Оставляем в формате Timestamp
            },
            {
                "Номер карты": "9876543210987654",
                "Сумма операции": 200.0,
                "Дата операции": pd.Timestamp("2021-01-02 14:00:00"),  # Оставляем в формате Timestamp
                "Сумма платежа": 180.0,
                "Дата платежа": pd.Timestamp("2021-01-02"),  # Оставляем в формате Timestamp
            },
        ]

        # Проверяем результат
        print(result)  # Для отладки
        self.assertEqual(result, expected_result)  # Сравниваем напрямую, уже в подходящем формате

        # Также проверим строки:
        expected_formatted = [
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": 100.0,
                "Дата операции": "01.01.2021 12:00:00",
                "Сумма платежа": 90.0,
                "Дата платежа": "01.01.2021",
            },
            {
                "Номер карты": "9876543210987654",
                "Сумма операции": 200.0,
                "Дата операции": "02.01.2021 14:00:00",
                "Сумма платежа": 180.0,
                "Дата платежа": "02.01.2021",
            },
        ]

        # Форматируем результат в строки, чтобы провести второе сравнение
        result_formatted = []
        for item in result:
            result_formatted.append(
                {
                    "Номер карты": item["Номер карты"],
                    "Сумма операции": item["Сумма операции"],
                    "Дата операции": item["Дата операции"].strftime("%d.%m.%Y %H:%M:%S"),
                    "Сумма платежа": item["Сумма платежа"],
                    "Дата платежа": item["Дата платежа"].strftime("%d.%m.%Y"),
                }
            )

        self.assertEqual(result_formatted, expected_formatted)  # Сравниваем отформатированные списки

    @patch("src.views.pd.read_excel")
    def test_load_operations_data_file_not_found(self, mock_read_excel):
        mock_read_excel.side_effect = FileNotFoundError
        result = load_operations_data("wrong_path.xlsx")
        self.assertEqual(result, [])  # Ожидаем пустой список

    @patch("src.views.pd.read_excel")
    def test_load_operations_data_value_error(self, mock_read_excel):
        mock_df = MagicMock()
        mock_df.to_dict.return_value = {
            "Номер карты": ["1234567890123456"],
            "Сумма операции": [100.0],
            "Дата операции": ["invalid_date_format"],
        }
        mock_read_excel.return_value = mock_df
        result = load_operations_data("fake_path.xlsx")
        self.assertEqual(result, [])  # Ожидаем пустой список из-за ошибки

    @patch("src.views.pd.read_excel")
    def test_load_operations_data_generic_exception(self, mock_read_excel):
        mock_read_excel.side_effect = Exception("Some error")
        result = load_operations_data("fake_path.xlsx")
        self.assertEqual(result, [])  # Ожидаем пустой список


class TestGenerateReport(unittest.TestCase):

    @patch("src.views.load_operations_data")
    @patch("src.views.calculate_cashback")
    @patch("src.views.get_currency_rates")
    @patch("src.views.get_stock_prices")
    @patch("src.views.get_greeting")
    @patch("src.views.create_json_response")
    def test_generate_report_success(
        self,
        mock_create_json_response,
        mock_get_greeting,
        mock_get_stock_prices,
        mock_get_currency_rates,
        mock_calculate_cashback,
        mock_load_operations_data,
    ):
        # Мокаем функцию, которая загружает операции
        mock_load_operations_data.return_value = [
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": 100.0,
                "Сумма платежа": 90.0,
                "Категория": "Продукты",
                "Описание": "Купил яблоки",
                "Дата платежа": pd.Timestamp("2021-01-01"),
            },
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": 200.0,
                "Сумма платежа": 180.0,
                "Категория": "Электроника",
                "Описание": "Купил телефон",
                "Дата платежа": pd.Timestamp("2021-01-02"),
            },
            {
                "Номер карты": "9876543210987654",
                "Сумма операции": 150.0,
                "Сумма платежа": 130.0,
                "Категория": "Бензин",
                "Описание": "Залил полный бак",
                "Дата платежа": pd.Timestamp("2021-01-03"),
            },
        ]

        # Устанавливаем логику кэшбека
        mock_calculate_cashback.side_effect = lambda x: x * 0.01  # 1% кэшбек
        mock_get_currency_rates.return_value = {"USD": 73.0}
        mock_get_stock_prices.return_value = {"AAPL": 150.0}
        mock_get_greeting.return_value = "Привет!"

        # Мокаем возвращаемый результат создания JSON
        mock_create_json_response.return_value = json.dumps(
            {
                "greeting": "Привет!",
                "cards": [
                    {"last_digits": "3456", "total_spent": 300.0, "cashback": 3.0},
                    {"last_digits": "7654", "total_spent": 150.0, "cashback": 1.5},
                ],
                "top_transactions": [
                    {"date": "02.01.2021", "amount": 180.0, "category": "Электроника", "description": "Купил телефон"},
                    {"date": "03.01.2021", "amount": 130.0, "category": "Бензин", "description": "Залил полный бак"},
                    {"date": "01.01.2021", "amount": 90.0, "category": "Продукты", "description": "Купил яблоки"},
                ],
                "currency_rates": {"USD": 73.0},
                "stock_prices": {"AAPL": 150.0},
            }
        )

        # Запускаем тестируемую функцию
        user_currencies = ["USD"]
        user_stocks = ["AAPL"]
        result = generate_report("fake_path.xlsx", user_currencies, user_stocks)

        # Проверяем результат
        expected_result = json.dumps(
            {
                "greeting": "Привет!",
                "cards": [
                    {"last_digits": "3456", "total_spent": 300.0, "cashback": 3.0},
                    {"last_digits": "7654", "total_spent": 150.0, "cashback": 1.5},
                ],
                "top_transactions": [
                    {"date": "02.01.2021", "amount": 180.0, "category": "Электроника", "description": "Купил телефон"},
                    {"date": "03.01.2021", "amount": 130.0, "category": "Бензин", "description": "Залил полный бак"},
                    {"date": "01.01.2021", "amount": 90.0, "category": "Продукты", "description": "Купил яблоки"},
                ],
                "currency_rates": {"USD": 73.0},
                "stock_prices": {"AAPL": 150.0},
            }
        )

        self.assertEqual(result, expected_result)
        mock_load_operations_data.assert_called_once_with("fake_path.xlsx")
        mock_calculate_cashback.assert_any_call(100.0)
        mock_calculate_cashback.assert_any_call(200.0)
        mock_calculate_cashback.assert_any_call(150.0)


if __name__ == "__main__":
    unittest.main()
