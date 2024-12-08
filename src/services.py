import logging

import pandas as pd


def analyze_cashback(data: str, year: int, month: int) -> dict:
    try:
        df = pd.read_excel(data)
    except Exception as e:
        logging.error(f"Ошибка при загрузке данных: {e}")
        return {}  # Возвращаем пустой словарь вместо JSON-строки

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

    # Проверка загруженных данных
    logging.info("Исходные данные:\n%s", df.head())

    # Фильтрация по году и месяцу
    filtered_data = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]

    # Проверка отфильтрованных данных
    logging.info("Отфильтрованные данные:\n%s", filtered_data.head())

    if filtered_data.empty:
        logging.warning("Нет данных для указанных года и месяца.")
        return {}  # Возвращаем пустой словарь

    # Группировка данных и суммирование кэшбэка
    cashback_per_category = filtered_data.groupby("Категория")["Кэшбэк"].sum().reset_index()
    cashback_dict = {row["Категория"]: int(row["Кэшбэк"]) for _, row in cashback_per_category.iterrows()}

    return cashback_dict  # Возвращаем словарь вместо JSON-строки


# Пример использования
if __name__ == "__main__":
    result = analyze_cashback("../data/operations.xlsx", 2021, 11)
    print(result)
