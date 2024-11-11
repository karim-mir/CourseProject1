from datetime import datetime, timedelta

import pytest

from src.views import get_start_and_end_dates, is_valid_datetime


@pytest.fixture
def date_times():
    return [
        (datetime(2024, 11, 11, 14, 12, 31), "W"),  # Тестовая дата для недели
        (datetime(2024, 11, 11, 14, 12, 31), "M"),  # Тестовая дата для месяца
        (datetime(2024, 11, 11, 14, 12, 31), "Y"),  # Тестовая дата для года
        (datetime(2024, 11, 11, 14, 12, 31), "ALL"),  # Тестовая дата для всех периодов
    ]


def test_get_start_and_end_dates(date_times):
    for input_date_time, period in date_times:
        start_date, end_date = get_start_and_end_dates(input_date_time, period)

        if period == "W":
            expected_start = input_date_time - timedelta(days=input_date_time.weekday())
            expected_end = expected_start + timedelta(days=6)
        elif period == "M":
            expected_start = input_date_time.replace(day=1)
            expected_end = input_date_time
        elif period == "Y":
            expected_start = input_date_time.replace(month=1, day=1)
            expected_end = input_date_time
        elif period == "ALL":
            expected_start = datetime(2010, 1, 1)
            expected_end = input_date_time
        else:
            expected_start = input_date_time.replace(day=1)
            expected_end = input_date_time

        assert start_date == expected_start
        assert end_date == expected_end


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("2024-11-11 14:12:31", True),
        ("2024-11-11 14:12:61", False),  # Неверная секунда
        ("2024-11-11", False),  # Неверный формат (без времени)
        ("invalid-date-time", False),  # Полностью неверный формат
    ],
)
def test_is_valid_datetime(test_input, expected):
    assert is_valid_datetime(test_input) == expected


if __name__ == "__main__":
    pytest.main()
