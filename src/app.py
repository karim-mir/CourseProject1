import concurrent.futures
import logging
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from src.views import get_currency_data, get_stock_data

load_dotenv()
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Корневой маршрут
@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Financial API!"


@app.route("/currency", methods=["GET"])
def currency():
    try:
        logging.debug("Fetching currency data")
        currency_data = get_currency_data()
        return jsonify(currency_data), 200
    except Exception as e:
        logging.error("Error fetching currency data: %s", e)
        return jsonify({"error": f"Failed to fetch currency data: {str(e)}"}), 500


@app.route("/stock/<symbol>", methods=["GET"])
def get_stock(symbol):
    try:
        data = get_stock_data(symbol)
        return jsonify(data), 200
    except ValueError as e:
        app.logger.error("Error fetching stock data: %s", str(e))
        return jsonify({"error": "Stock not found"}), 404
    except Exception as e:
        app.logger.error("Error fetching stock data: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


# Пример данных о картах
cards = [{"number": "1234567812345814", "expenses": [1200, 62]}, {"number": "9876543210987512", "expenses": [7.94]}]

# Пример транзакций
transactions = [
    {
        "date": "2021-12-21",
        "amount": 1198.23,
        "category": "Переводы",
        "description": "Перевод Кредитная карта. ТП 10.2 RUR",
    },
    {"date": "2021-12-20", "amount": 829.00, "category": "Супермаркеты", "description": "Лента"},
]


def get_greeting(current_time):
    if current_time.hour < 6:
        return "Доброй ночи"
    elif current_time.hour < 12:
        return "Доброе утро"
    elif current_time.hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


def calculate_cashback(expenses):
    return sum(expenses) / 100  # 1 рубль на каждые 100 рублей


def get_top_transactions():
    return sorted(transactions, key=lambda x: x["amount"], reverse=True)[:5]


@app.route("/api/data", methods=["GET"])
def get_data():
    date_time_str = request.args.get("date_time")
    if not date_time_str:
        return jsonify({"error": "Date and time string is required"}), 400

    try:
        current_time = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

    greeting = get_greeting(current_time)

    # Получение информации по картам
    card_info = []
    for card in cards:
        last4 = card["number"][-4:]  # последние 4 цифры карты
        total_spent = sum(card["expenses"])  # Общая сумма расходов
        cashback = calculate_cashback(card["expenses"])  # Кэшбэк
        card_info.append({"last_digits": last4, "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)})

    top_transactions = get_top_transactions()

    try:
        currency_rates = get_currency_data()  # Получение данных о курсах валют
        stock_symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        stock_prices = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_symbol = {executor.submit(get_stock_data, symbol): symbol for symbol in stock_symbols}
            for future in concurrent.futures.as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    stock_prices.append(future.result())
                except Exception as e:
                    logging.error(f"Error fetching stock price for {symbol}: {e}")
                    stock_prices.append({"symbol": symbol, "error": str(e)})
    except Exception as e:
        logging.error("Error fetching stock data or currency rate: %s", e)
        return jsonify({"error": "Failed to fetch stock price or currency rate: " + str(e)}), 500

    return jsonify(
        {
            "greeting": greeting,
            "cards": card_info,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
