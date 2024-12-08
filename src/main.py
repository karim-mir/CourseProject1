import os
from datetime import datetime

import pandas as pd

from src.reports import spending_by_category
from src.services import analyze_cashback
from src.utils import calculate_cashback, get_currency_rates, get_greeting, get_stock_prices, load_user_settings
from src.views import create_json_response, load_operations_data


def process_operations(operations):
    transactions = []
    cards = {}

    # Логируем операции для отладки
    print("Загруженные операции:", operations)

    for operation in operations:
        # Проверка, что operation является словарем
        if not isinstance(operation, dict):
            print(f"Ожидался словарь, но получено: {operation}")
            continue

        # Проверяем наличие необходимых ключей и их значения
        card_number = operation.get("Номер карты")
        amount = operation.get("Сумма операции")

        # Проверка на nan
        if pd.isna(card_number) or pd.isna(amount):
            print(f"Недостаточно данных для обработки операции: {operation}")
            continue

        # Обработка суммы
        try:
            amount_float = float(amount)  # Преобразуем в float
        except ValueError:
            print(f"Ошибка преобразования суммы: {amount}. Пропускаем эту операцию.")
            continue

        # Сохраняем данные по картам
        if card_number not in cards:
            cards[card_number] = {
                "last_digits": card_number[-4:],  # Последние 4 цифры
                "total_spent": 0,
                "cashback": 0,
            }

        # Обновляем итоги
        cards[card_number]["total_spent"] += abs(amount_float)
        cards[card_number]["cashback"] += calculate_cashback(abs(amount_float))

        # Добавляем информацию о транзакции
        transaction_date = operation.get("Дата операции")
        if isinstance(transaction_date, (str, pd.Timestamp)):
            # Приводим дату к нужному формату
            if isinstance(transaction_date, pd.Timestamp):
                transaction_date = transaction_date.strftime("%d.%m.%Y")
            transactions.append(
                {
                    "date": transaction_date,
                    "amount": amount_float,
                    "category": operation.get("Категория", "Неизвестно"),
                    "description": operation.get("Описание", "Нет описания"),
                }
            )
        else:
            print(f"Неверный формат даты: {transaction_date}. Пропускаем эту транзакцию.")

    return list(cards.values()), transactions


def main():
    user_settings_path = os.path.join("..", "user_settings.json")
    user_settings = load_user_settings(user_settings_path)

    try:
        input_date = input("Введите дату в формате YYYY-MM-DD HH:MM:SS: ")
        date_input = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")

        print(f"Тип date_input: {type(date_input)}")
        greeting = get_greeting()

        # Загрузка данных операций
        file_path = os.path.join("..", "data", "operations.xlsx")
        operations = load_operations_data(file_path)
        cards_list, transactions = process_operations(operations)

        # Сортировка и получение топ-5 транзакций
        top_transactions = sorted(transactions, key=lambda x: x["amount"], reverse=True)[:5]

        # Загрузка курсов валют и цен акций
        currency_rates = get_currency_rates(user_settings["user_currencies"])
        stock_prices = get_stock_prices(user_settings["user_stocks"])

        # Создание JSON-ответа
        json_response = create_json_response(greeting, cards_list, top_transactions, currency_rates, stock_prices)

        # Печать JSON-ответа
        print("JSON Ответ:")
        print(json_response)

        # Вызов функции analyze_cashback из services.py
        cashback_report = analyze_cashback(file_path, date_input.year, date_input.month)
        if not isinstance(cashback_report, dict):
            raise ValueError("Ожидался словарь в отчете по кешбэку.")

        print("Отчет по кешбэку:")
        print(cashback_report)

        # Вызов функции spending_by_category из reports.py (пример для категории)
        # Если вы хотите проанализировать конкретную категорию, вы можете указать её в качестве аргумента
        category_to_check = "Супермаркеты"  # Замените на нужную категорию
        spending_report = spending_by_category(pd.DataFrame(operations), category_to_check)
        print(f"Отчет по тратам для категории '{category_to_check}':")
        print(spending_report.to_dict(orient="records"))

    except ValueError as ve:
        print(f"Ошибка значения: {ve}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
