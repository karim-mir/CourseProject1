import json
import logging
from typing import Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def save_report(file_name: str = "my_json.json"):
    """
    Декоратор для сохранения отчетов в файл
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)  # Получаем результат функции

            # Преобразуем датафрейм для сериализации
            result["Дата платежа"] = result["Дата платежа"].dt.strftime("%Y-%m-%d %H:%M:%S")

            # Сохраняем результат в JSON-файл
            with open(file_name, "w") as f:
                json.dump(result.to_dict(orient="records"), f, ensure_ascii=False, indent=4)
            logging.info(f"Отчет сохранен в файл: {file_name}")
            return result

        return wrapper

    return decorator


@save_report()  # Используется имя файла по умолчанию
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    # Преобразуем столбец 'Дата платежа' в datetime
    transactions["Дата платежа"] = pd.to_datetime(transactions["Дата платежа"], format="%d.%m.%Y", errors="coerce")

    # Проверка введенной даты
    if date is None:
        date = transactions["Дата платежа"].max()
    else:
        date = pd.to_datetime(date)

    three_months_ago = date - pd.DateOffset(months=3)

    # Фильтруем данные по категории и дате
    filtered_data = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата платежа"] >= three_months_ago)
        & (transactions["Дата платежа"] <= date)
    ]

    return filtered_data[["Дата платежа", "Сумма операции", "Описание"]].copy()


# Пример создания DataFrame из файла Excel
transactions_df = pd.read_excel("../data/operations.xlsx")

# Вызываем функцию для получения отчета
result = spending_by_category(transactions_df, category="Супермаркеты")

# Печать результата
print("Отчет по тратам для категории 'Супермаркеты':")
print(result)
