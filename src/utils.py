import json
import logging
import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Загрузка переменных окружения
load_dotenv()

# Получение данных из переменных окружения
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCK_API_URL = os.getenv("STOCK_API_URL")
CURRENCY_API_URL = os.getenv("CURRENCY_API_URL")

if not STOCK_API_KEY or not CURRENCY_API_KEY:
    print("Warning: API keys are not set in the environment variables.")


def load_transactions() -> pd.DataFrame:
    # Ваши фиксированные данные
    data = {
        "date": ["2020-05-01", "2020-05-02", "2020-05-03", "2020-05-20", "2020-05-20"],
        "category": ["Food", "Transport", "Entertainment", "Food", "Transport"],
        "amount": [50, -20, -150, -75, -30],
        "description": ["Description 1", "Description 2", "Description 3", "Description 4", "Description 5"],
        "card": [
            "1234 5678 9876 5432",
            "1234 5678 9876 5433",
            "1234 5678 9876 5434",
            "1234 5678 9876 5435",
            "1234 5678 9876 5436",
        ],
    }
    # Создаем DataFrame
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    return df  # Возвращаем все данные


def get_expenses(start_date, end_date) -> dict:
    # Загружаем все транзакции
    df = load_transactions()  # Получаем все данные

    # Проверка и фильтрация данных по дате
    filtered_transactions = df[(df["date"] >= start_date) & (df["date"] <= end_date) & (df["amount"] < 0)]
    total_amount = -filtered_transactions["amount"].sum()

    # Группируем по категориям
    category_groups = filtered_transactions.groupby("category")["amount"].sum().reset_index()
    category_groups["amount"] = -category_groups["amount"]  # Делает суммы положительными для удобства

    main_expenses = category_groups.nlargest(7, "amount").to_dict(orient="records")

    # Суммируем остальные категории
    remaining_expenses = category_groups[
        ~category_groups["category"].isin([item["category"] for item in main_expenses])
    ]
    if not remaining_expenses.empty:
        others_amount = remaining_expenses["amount"].sum()
        main_expenses.append({"category": "Остальное", "amount": others_amount})

    return {"total_amount": round(total_amount), "main": main_expenses}


def get_income(start_date, end_date) -> dict:
    df = load_transactions()
    filtered_income = df[(df["date"] >= start_date) & (df["date"] <= end_date) & (df["amount"] > 0)]
    total_income = filtered_income["amount"].sum()

    # Группируем по категориям
    category_groups = filtered_income.groupby("category")["amount"].sum().reset_index()
    main_income = category_groups.nlargest(7, "amount").to_dict(orient="records")

    return {"total_amount": round(total_income), "main": main_income}


def get_currency_rates() -> list:
    try:
        url = f"{CURRENCY_API_URL}/latest?access_key={CURRENCY_API_KEY}&base=USD"
        response = requests.get(url)
        response.raise_for_status()  # Вызывает исключение для некорректных ответов
        data = response.json()
        rates = data.get("rates", {})
        return [{"currency": currency, "rate": rate} for currency, rate in rates.items()]

    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Error Occurred: {err}")

    return []


def get_stock_prices(stock_symbol: str) -> dict:
    stocks = stock_symbol.split(",")
    stock_data = []

    for stock in stocks:
        stock = stock.strip()
        try:
            response = requests.get(
                f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={STOCK_API_KEY}"
            )
            if response.status_code != 200:
                logging.error(f"Error fetching data: {response.status_code}")
                return None

            logging.info(f"Request URL: {response.url}")
            logging.info(f"Response Status Code: {response.status_code}")
            data = response.json()
            logging.info(f"Response Data: {data}")

            if "Time Series (Daily)" not in data:
                logging.error("No daily time series data found.")
                return None

            time_series = data["Time Series (Daily)"]
            # Пример получения цен за последние 2 дня
            for date, metrics in list(time_series.items())[:2]:  # Получаем данные за 2 последних дня
                open_price = float(metrics["1. open"])
                close_price = float(metrics["4. close"])
                volume = int(metrics["5. volume"])
                stock_data.append(
                    {
                        "date": date,
                        "stock": stock,
                        "open": round(open_price, 2),
                        "close": round(close_price, 2),
                        "volume": volume,
                    }
                )

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for {stock}: {e}")

    return stock_data


def fetch_data(date_str, date_range="M", stock_symbol="AAPL"):
    # Конвертация входной строки даты в объект даты
    date_format = "%Y-%m-%d"
    given_date = datetime.strptime(date_str, date_format)

    # Определение начала и конца диапазона
    if date_range == "W":
        start_date = given_date - timedelta(days=given_date.weekday())  # Дата начала недели
        end_date = given_date
    elif date_range == "M":
        start_date = given_date.replace(day=1)  # Начало месяца
        end_date = given_date
    elif date_range == "Y":
        start_date = given_date.replace(month=1, day=1)  # Начало года
        end_date = given_date
    elif date_range == "ALL":
        start_date = datetime(2020, 1, 1)  # Или любой другой начальный момент
        end_date = given_date
    else:
        raise ValueError("Некорректный диапазон данных")

    # Запрос данных
    return {
        "expenses": get_expenses(start_date, end_date),
        "income": get_income(start_date, end_date),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(stock_symbol),  # Передаем stock_symbol
    }


if __name__ == "__main__":
    # Пример вызова функции
    date_str = "2024-11-08"
    try:
        result = fetch_data(date_str, "M")
        print(json.dumps(result, indent=4, ensure_ascii=False))
    except ValueError as e:
        logging.error(f"ValueError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
