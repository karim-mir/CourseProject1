from pathlib import Path
import pandas as pd
import json
import pytest
from src.services import analyze_cashback

@pytest.fixture
def create_test_data(tmp_path):
    # Создание тестового Excel файла
    data = {
        'Дата операции': ['01.11.2021 10:00:00', '05.11.2021 12:00:00', '10.11.2021 14:00:00'],
        'Категория': ['Кафе', 'Кафе', 'Кино'],
        'Кэшбэк': [100, 50, 30]
    }

    df = pd.DataFrame(data)
    test_file = tmp_path / "test_operations.xlsx"
    df.to_excel(test_file, index=False)

    return str(test_file)

def test_analyze_cashback_with_valid_data(create_test_data):
    result = analyze_cashback(create_test_data, 2021, 11)
    expected_output = json.dumps({"Кафе": 150, "Кино": 30}, ensure_ascii=False)
    assert result == expected_output

def test_analyze_cashback_no_transactions(create_test_data):
    # Создание тестового файла без транзакций
    empty_data = {
        'Дата операции': [],
        'Категория': [],
        'Кэшбэк': []
    }
    df = pd.DataFrame(empty_data)
    test_file = Path(create_test_data).parent / "empty_operations.xlsx"
    df.to_excel(test_file, index=False)

    result = analyze_cashback(str(test_file), 2021, 11)
    expected_output = json.dumps({}, ensure_ascii=False)
    assert result == expected_output

def test_analyze_cashback_error_loading_file():
    # Тестирование обработки ошибок для несуществующего файла
    result = analyze_cashback("non_existent_file.xlsx", 2021, 11)
    expected_output = json.dumps({}, ensure_ascii=False)
    assert result == expected_output

def test_analyze_cashback_different_format_dates(create_test_data):
    # Здесь мы используем pathlib для создания пути
    test_file = Path(create_test_data).parent / "test_operations_different_format.xlsx"

    # Сохраняем данные в новый файл
    df = pd.read_excel(create_test_data)
    df.to_excel(test_file, index=False)

    # Вызываем функцию
    result = analyze_cashback(str(test_file), 2021, 11)
    expected_output = json.dumps({"Кафе": 150, "Кино": 30}, ensure_ascii=False)

    assert result == expected_output
