import unittest
from unittest.mock import MagicMock, patch

from src.main import handle_events_page, handle_main_page, validate_datetime


class TestMainModule(unittest.TestCase):

    @patch("src.main.datetime")
    def test_validate_datetime_success(self, mock_datetime):
        # Подготовка
        mock_datetime.strptime = MagicMock(return_value="mocked_datetime")

        # Проверка исправного ввода
        result = validate_datetime("2024-08-25 13:00:00")
        self.assertEqual(result, "mocked_datetime")

    @patch("src.main.datetime")
    def test_validate_datetime_failure(self, mock_datetime):
        # Настройка для того, чтобы strptime выбрасывал исключение
        mock_datetime.strptime.side_effect = ValueError

        # Проверка ошибочного ввода
        result = validate_datetime("invalid_date_time")
        self.assertIsNone(result)

    @patch("src.main.input", side_effect=["2024-08-25 13:00:00", "AAPL, GOOG"])  # Дата  # Символы акций
    @patch("src.views.main_page", return_value="Response from main_page")
    def test_handle_main_page(self, mock_main_page, mock_input):
        handle_main_page()
        # Проверка, что функция main_page была вызвана с ожидаемыми аргументами.
        mock_main_page.assert_called_with("2024-08-25 13:00:00", ["AAPL", "GOOG"])

    @patch("src.main.input", side_effect=["2024-08-25 13:00:00", ""])  # Дата  # Пустой ввод для периода
    @patch("src.views.events_page", return_value="Response from events_page")
    def test_handle_events_page(self, mock_events_page, mock_input):
        handle_events_page()
        mock_events_page.assert_called_with("2024-08-25 13:00:00", "M")  # Период по умолчанию "M"


if __name__ == "__main__":
    unittest.main()
