import json
import logging
from datetime import datetime

import pandas as pd

from src.utils import get_currency_rates, get_stock_prices, load_transactions


def get_greeting() -> str:
    """Возвращает приветствие в зависимости от текущего времени суток."""
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def create_json_response(data):
    """Формирует JSON-ответ из переданных данных."""
    return json.dumps(data, ensure_ascii=False)


def main_page(date_str: str, stock_symbol: str = None):
    """Формация главной страницы с данными о транзакциях, курсах валют и ценах акций."""
    # Добавьте часы, минуты и секунды, если они отсутствуют
    if len(date_str) == 10:  # YYYY-MM-DD
        date_str += " 00:00:00"

    if not is_valid_datetime(date_str):
        return create_json_response({"error": "Неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS."})

    # Логика загрузки транзакций
    transactions = load_transactions(date_str)

    if transactions.empty:
        return create_json_response({"error": "Данные транзакций отсутствуют."})

    # Используем transactions вместо transactions_df
    card_groups = transactions.groupby("card")["amount"].agg(total_spent="sum").reset_index()
    cards_info = [
        {
            "last_digits": row["card"][-4:],
            "total_spent": round(row["total_spent"], 2),
            "cashback": round(row["total_spent"] * 0.01, 2),
        }
        for _, row in card_groups.iterrows()
    ]

    top_transactions = (
        transactions.nlargest(5, "amount")[["date", "amount", "category", "description"]]
        .assign(date=lambda x: x["date"].dt.strftime("%d.%m.%Y"))
        .to_dict(orient="records")
    )

    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices(stock_symbol)

    greeting = get_greeting()  # Предполагается наличие этой функции

    response = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return create_json_response(response)


def events_page(date_time_str: str, period: str = "M") -> str:
    """Формирует страницу событий, представляя данные за указанный период."""
    # Проверка на валидность даты
    if not is_valid_datetime(date_time_str):
        return create_json_response({"error": "Неверный формат даты. Используйте YYYY-MM-DD HH:MM:SS."})

    input_date_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    start_date, end_date = get_start_and_end_dates(input_date_time, period)

    logging.info(f"Start date for filtering: {start_date}. End date: {end_date}.")

    transactions_df = load_transactions()
    transactions_df["date"] = pd.to_datetime(transactions_df["date"])

    logging.info(f"Loaded transactions: {len(transactions_df)} records.")
    logging.info(f"Transaction dates: {transactions_df['date'].dt.strftime('%Y-%m-%d %H:%M:%S').unique()}")

    if transactions_df.empty:
        return create_json_response({"error": "Данные транзакций отсутствуют."})

    filtered_df = transactions_df[(transactions_df["date"] >= start_date) & (transactions_df["date"] <= end_date)]

    logging.info(f"Filtered transactions: {filtered_df.to_dict(orient='records')}")

    if filtered_df.empty:
        return create_json_response({"error": "Нет данных за указанный период."})

    total_expenses = filtered_df[filtered_df["amount"] < 0]["amount"].sum()
    total_income = filtered_df[filtered_df["amount"] > 0]["amount"].sum()

    main_expenses = (
        filtered_df[filtered_df["amount"] < 0].groupby("category")["amount"].sum().nlargest(6).reset_index()
    )
    main_expenses["amount"] = (
        main_expenses["amount"].astype(float).abs()
    )  # Преобразуем к float и берем положительное значение

    main_income = filtered_df[filtered_df["amount"] > 0].groupby("category")["amount"].sum().nlargest(3).reset_index()

    main_income["amount"] = main_income["amount"].astype(float)  # Преобразуем к float

    currency_rates = get_currency_rates()
    stock_prices = get_stock_prices("AAPL")

    response = {
        "expenses": {
            "total_amount": float(total_expenses),
            "main": main_expenses.to_dict(orient="records"),
        },
        "income": {
            "total_amount": float(total_income),
            "main": main_income.to_dict(orient="records"),
        },
        "currency_rates": currency_rates,
        "stock_prices": stock_prices if stock_prices is not None else {"error": "Could not retrieve stock prices"},
    }
    logging.info(f"Response data: {response}")

    return create_json_response(response)


def get_start_and_end_dates(input_date_time: datetime, period: str) -> (datetime, datetime):
    """Возвращает начальную и конечную даты для заданного периода."""
    if period == "W":
        start_date = input_date_time - pd.Timedelta(days=input_date_time.weekday())
        end_date = start_date + pd.Timedelta(days=6)
    elif period == "M":
        start_date = input_date_time.replace(day=1)
        end_date = input_date_time
    elif period == "Y":
        start_date = input_date_time.replace(month=1, day=1)
        end_date = input_date_time
    elif period == "ALL":
        start_date = datetime(2010, 1, 1)
        end_date = input_date_time
    else:
        start_date = input_date_time.replace(day=1)
        end_date = input_date_time

    return start_date, end_date


def is_valid_datetime(dt_str: str) -> bool:
    """Проверяет, является ли строка даты и времени валидной."""
    try:
        # Проверяем формат с учетом времени
        datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False
