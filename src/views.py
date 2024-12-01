import json
import logging
import os

import pandas as pd

from src.utils import calculate_cashback, get_currency_rates, get_greeting, get_stock_prices

logging.basicConfig(level=logging.INFO)

file_path = os.path.abspath(os.path.join("..", "data", "operations.xlsx"))


def create_json_response(greeting, cards, top_transactions, currency_rates, stock_prices):
    response = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    return json.dumps(response, ensure_ascii=False, indent=2)


def load_operations_data(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Исходный DataFrame:", df.head())  # Вывод начального состояния

        # Преобразуем даты
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
        df["Дата платежа"] = pd.to_datetime(df["Дата платежа"], format="%d.%m.%Y", errors="coerce")

        print("После преобразования дат:", df[["Дата операции", "Дата платежа"]].head())  # Вывод состояния дат

        # Преобразование типов столбцов
        df["Сумма операции"] = df["Сумма операции"].astype(float)
        df["Сумма платежа"] = df["Сумма платежа"].astype(float)

        # Проверка после преобразования
        print("После преобразования сумм:", df[["Сумма операции", "Сумма платежа"]].head())

        # Проверьте наличие нужных столбцов перед преобразованием в словари
        if not all(
            col in df.columns
            for col in ["Номер карты", "Сумма операции", "Дата операции", "Сумма платежа", "Дата платежа"]
        ):
            raise ValueError("Недостаточно данных в DataFrame")

        operations = df.to_dict(orient="records")
        logging.info("Данные успешно загружены из файла Excel.")
        return operations
    except FileNotFoundError:
        logging.error(f"Файл не найден: {file_path}")
        return []
    except ValueError as e:
        logging.error(f"Ошибка обработки данных: {e}")
        return []
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return []


def generate_report(file_path, user_currencies, user_stocks):
    operations = load_operations_data(file_path)

    if not operations:
        return create_json_response("Ошибка загрузки данных", [], [], [], [])

    # Остальная логика формирования отчета остается без изменений
    cards_data = {}
    for op in operations:
        card_number = op["Номер карты"]
        total_spent = cards_data.get(card_number, {"total_spent": 0, "cashback": 0})
        total_spent["total_spent"] += op["Сумма операции"]
        total_spent["cashback"] += calculate_cashback(op["Сумма операции"])  # Используем функцию из utils
        cards_data[card_number] = total_spent

    cards = [
        {
            "last_digits": str(card)[-4:],
            "total_spent": round(data["total_spent"], 2),
            "cashback": round(data["cashback"], 2),
        }
        for card, data in cards_data.items()
    ]

    # Формируем топ-5 транзакций
    top_transactions = sorted(operations, key=lambda x: x["Сумма платежа"], reverse=True)[:5]
    top_transactions = [
        {
            "date": op["Дата платежа"].strftime("%d.%m.%Y"),
            "amount": round(op["Сумма платежа"], 2),
            "category": op["Категория"],
            "description": op["Описание"],
        }
        for op in top_transactions
    ]

    # Получаем курсы валют и цены акций
    currency_rates = get_currency_rates(user_currencies)
    stock_prices = get_stock_prices(user_stocks)

    greeting = get_greeting()

    return create_json_response(greeting, cards, top_transactions, currency_rates, stock_prices)


# Пример использования функции
if __name__ == "__main__":
    user_currencies = ["USD", "EUR"]  # Пример списка валют
    user_stocks = ["AAPL", "AMZN"]  # Пример списка акций
    json_response = generate_report(
        os.path.abspath(os.path.join("..", "data", "operations.xlsx")), user_currencies, user_stocks
    )
    print(json_response)
