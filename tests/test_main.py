import unittest
from unittest.mock import patch

from src.main import process_operations


class TestMain(unittest.TestCase):

    @patch("src.utils.calculate_cashback")
    def test_process_operations(self, mock_calculate_cashback):
        # Настройка мока для calculate_cashback
        mock_calculate_cashback.side_effect = lambda amount: amount * 0.01  # Предполагаем что кэшбэк 1%

        operations = [
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": 100.0,
                "Дата операции": "01.01.2021",
                "Категория": "Покупки",
                "Описание": "Купить что-то",
            },
            {
                "Номер карты": "9876543210987654",
                "Сумма операции": 200.0,
                "Дата операции": "02.01.2021",
                "Категория": "Билеты",
                "Описание": "Купить билет",
            },
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": -50.0,
                "Дата операции": "01.01.2021",
                "Категория": "Возврат",
                "Описание": "",
            },
            {"Номер карты": None, "Сумма операции": 150.0, "Дата операции": "03.01.2021"},  # тест на None
            {
                "Номер карты": "1234567890123456",
                "Сумма операции": "не число",  # тест на ValueError
                "Дата операции": "04.01.2021",
                "Категория": "Покупки",
                "Описание": "Купить что-то еще",
            },
        ]

        expected_cards = [
            {"last_digits": "3456", "total_spent": 150.0, "cashback": 1.5},  # 1% от 150
            {"last_digits": "7654", "total_spent": 200.0, "cashback": 2.0},  # 1% от 200
        ]

        expected_transactions = [
            {"date": "01.01.2021", "amount": 100.0, "category": "Покупки", "description": "Купить что-то"},
            {"date": "02.01.2021", "amount": 200.0, "category": "Билеты", "description": "Купить билет"},
            {"date": "01.01.2021", "amount": -50.0, "category": "Возврат", "description": ""},
        ]

        cards_list, transactions = process_operations(operations)

        self.assertEqual(cards_list, expected_cards)
        self.assertEqual(transactions, expected_transactions)


if __name__ == "__main__":
    unittest.main()
