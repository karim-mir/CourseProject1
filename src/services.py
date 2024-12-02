import pandas as pd
import json
import logging


def analyze_cashback(data: str, year: int, month: int) -> str:
    try:
        df = pd.read_excel(data)
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
        return json.dumps({}, ensure_ascii=False)

    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S', errors='coerce')

    # Проверка загруженных данных
    print("Исходные данные:\n", df)

    # Фильтрация по году и месяцу
    filtered_data = df[(df['Дата операции'].dt.year == year) & (df['Дата операции'].dt.month == month)]

    # Проверка отфильтрованных данных
    print("Отфильтрованные данные:\n", filtered_data)

    if filtered_data.empty:
        logging.warning("Нет данных для указанных года и месяца.")
        return json.dumps({}, ensure_ascii=False)

    # Группировка данных и суммирование кэшбэка
    cashback_per_category = filtered_data.groupby('Категория')['Кэшбэк'].sum().reset_index()
    cashback_dict = {row['Категория']: int(row['Кэшбэк']) for _, row in cashback_per_category.iterrows()}

    return json.dumps(cashback_dict, ensure_ascii=False)

# Пример использования
if __name__ == "__main__":
    result = analyze_cashback( '../data/operations.xlsx', 2021, 11)
    print(result)
