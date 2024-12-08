import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

file_path = os.path.abspath(os.path.join("..", "data", "operations.xlsx"))

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
STOCK_API_URL = os.getenv("STOCK_API_URL")
CURRENCY_API_URL = os.getenv("CURRENCY_API_URL")


def load_user_settings(file_path):
    with open(file_path, "r") as file:
        settings = json.load(file)
    return settings


def get_greeting():
    hour = datetime.now().hour
    if hour < 6:
        return "Доброй ночи"
    elif hour < 12:
        return "Доброе утро"
    elif hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


def get_currency_rates(user_currencies):
    rates = []
    for currency in user_currencies:
        url = f"{CURRENCY_API_URL}/latest?access_key={CURRENCY_API_KEY}&symbols={currency}"
        print(f"Запрос к: {url}")  # Логирование запроса
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Response data:", data)  # Логируем полученные данные
            if "rates" in data and isinstance(data["rates"], dict):
                if currency in data["rates"]:
                    rates.append({"currency": currency, "rate": data["rates"][currency]})
                else:
                    print(f"Курс не найден для {currency}. Ответ: {data}")
            else:
                print(f"'rates' отсутствует или не является словарем. Ответ: {data}")
        else:
            print(f"Ошибка API: {response.status_code}. Ответ: {response.text}")
    return rates


def get_stock_prices(user_stocks):
    prices = []
    for stock in user_stocks:
        url = (
            f"{STOCK_API_URL}/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=1min&apikey={STOCK_API_KEY}"
        )
        print(f"Запрос к: {url}")  # Логирование запроса
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Response data:", data)  # Логируем полученные данные
            time_series_key = "Time Series (1min)"
            if time_series_key in data and isinstance(data[time_series_key], dict):
                latest_time = next(iter(data[time_series_key]))  # Получаем последнее время
                latest_price = data[time_series_key][latest_time]["1. open"]
                prices.append({"stock": stock, "price": float(latest_price)})
            else:
                print(f"'Time Series (1min)' отсутствует или не является словарем. Ответ: {data}")
        else:
            print(f"Ошибка API: {response.status_code}. Ответ: {response.text}")
    return prices


def calculate_cashback(total_spent):
    return total_spent * 0.01
