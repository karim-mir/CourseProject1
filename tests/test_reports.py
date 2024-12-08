import unittest
from unittest.mock import patch

import pandas as pd

from src.reports import spending_by_category


class TestReports(unittest.TestCase):

    def setUp(self):
        # Создание фиктивных данных
        data = {
            "Дата платежа": ["01.05.2021", "15.05.2021", "20.06.2021", "10.07.2021"],
            "Сумма операции": [100, 200, 150, 300],
            "Категория": ["Супермаркеты", "Рестораны", "Супермаркеты", "Супермаркеты"],
            "Описание": ["Покупка в магазине", "Ужин с друзьями", "Магазин продуктов", "Еще один магазин"],
        }
        self.transactions_df = pd.DataFrame(data)
        self.transactions_df["Дата платежа"] = pd.to_datetime(self.transactions_df["Дата платежа"], format="%d.%m.%Y")

    @patch("src.reports.logging.info")  # Патч для логирования
    def test_spending_by_category_with_valid_data(self, mock_logging_info):
        category = "Супермаркеты"
        expected_data = {
            "Дата платежа": pd.to_datetime(["01.05.2021", "20.06.2021", "10.07.2021"], format="%d.%m.%Y"),
            "Сумма операции": [100, 150, 300],
            "Описание": ["Покупка в магазине", "Магазин продуктов", "Еще один магазин"],
        }
        expected_df = pd.DataFrame(expected_data)

        result = spending_by_category(self.transactions_df, category)

        # Приведите столбец "Сумма операции" к int и дату к нужному типу
        result["Дата платежа"] = pd.to_datetime(result["Дата платежа"])
        result["Сумма операции"] = result["Сумма операции"].astype(int)

        # Проверяем результат
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df.reset_index(drop=True))

    def test_spending_by_category_with_no_data(self):
        category = "Не существующая категория"
        expected_df = pd.DataFrame(columns=["Дата платежа", "Сумма операции", "Описание"])

        result = spending_by_category(self.transactions_df, category)

        # Принудительное приведение типа столбца "Сумма операции" к object
        result["Сумма операции"] = result["Сумма операции"].astype(object)

        # Проверяем результат (должен быть пустой DataFrame)
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df)

    def test_spending_by_category_particular_case(self):
        category = "Супермаркеты"
        expected_data = {
            "Дата платежа": pd.to_datetime(["01.05.2021"], format="%d.%m.%Y"),
            "Сумма операции": [100],
            "Описание": ["Покупка в магазине"],
        }
        expected_df = pd.DataFrame(expected_data)

        filtered_df = self.transactions_df[self.transactions_df["Сумма операции"] == 100]
        result = spending_by_category(filtered_df, category)

        result["Дата платежа"] = pd.to_datetime(result["Дата платежа"])
        result["Сумма операции"] = result["Сумма операции"].astype(int)

        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_df.reset_index(drop=True))


if __name__ == "__main__":
    unittest.main()
