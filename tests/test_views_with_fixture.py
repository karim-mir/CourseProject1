import json
import os
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import generate_report

# Путь к тестовым данным
TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "test_operations.xlsx")


@pytest.fixture
def operations_data():
    # Создадим тестовый и временный DataFrame и сохраним его в Excel
    data = {
        "Номер карты": [1234567812345678] * 5,
        "Сумма операции": [100.0, 200.0, 150.0, 250.0, 300.0],
        "Дата операции": [
            "01.12.2021 10:00:00",
            "02.12.2021 11:00:00",
            "03.12.2021 12:00:00",
            "04.12.2021 13:00:00",
            "05.12.2021 14:00:00",
        ],
        "Сумма платежа": [100.0, 200.0, 150.0, 250.0, 300.0],
        "Дата платежа": [
            "01.12.2021",
            "02.12.2021",
            "03.12.2021",
            "04.12.2021",
            "05.12.2021",
        ],
        "Категория": ["Еда", "Развлечения", "Транспорт", "Покупки", "Техника"],
        "Описание": ["Покупка 1", "Покупка 2", "Покупка 3", "Покупка 4", "Покупка 5"],
    }
    df = pd.DataFrame(data)
    df.to_excel(TEST_DATA_PATH, index=False, engine="openpyxl")  # Сохраним в Excel

    yield TEST_DATA_PATH  # Вернем путь к тестовым данным

    # После теста удалим тестовый файл
    os.remove(TEST_DATA_PATH)


def test_generate_report(operations_data):
    user_currencies = ["USD", "EUR"]
    user_stocks = ["AAPL", "AMZN"]

    with patch("src.utils.calculate_cashback") as mock_calculate_cashback:
        mock_calculate_cashback.return_value = 5.0  # Предположим, что кэшбэк всегда 5

        json_response = generate_report(operations_data, user_currencies, user_stocks)

        # Проверяем, что ответ имеет нужные ключи
        response_data = json.loads(json_response)
        assert "greeting" in response_data
        assert "cards" in response_data
        assert "top_transactions" in response_data
        assert "currency_rates" in response_data
        assert "stock_prices" in response_data

        # Проверяем, что топ-5 транзакций возвращает правильные данные
        assert len(response_data["top_transactions"]) == 5
        assert response_data["top_transactions"][0]["amount"] == 300.0  # Проверяем наибольшую сумму платежа
        assert round(response_data["cards"][0]["total_spent"], 2) == 1000.0  # Проверяем общую сумму по картам


if __name__ == "__main__":
    pytest.main()
