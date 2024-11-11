from datetime import datetime

from src.views import events_page, main_page


def validate_datetime(input_str):
    """Проверяет, является ли введенная строка корректной датой и временем."""
    try:
        return datetime.strptime(input_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def handle_main_page():
    """Обрабатывает действия на главной странице и выводит информацию о транзакциях, курсах валют и ценах акций."""
    print("Starting handle_main_page")
    date_time_input = input("Введите дату и время (YYYY-MM-DD HH:MM:SS): ")
    valid_date_time = validate_datetime(date_time_input)

    while not valid_date_time:
        print("Неверный формат даты и времени. Попробуйте снова.")
        date_time_input = input("Введите дату и время (YYYY-MM-DD HH:MM:SS): ")
        valid_date_time = validate_datetime(date_time_input)

    while True:
        stock_symbol_input = input("Введите символ акции (или несколько через запятую): ").strip()
        if stock_symbol_input:
            stock_symbols = [s.strip() for s in stock_symbol_input.split(",")]
            break
        else:
            print("Символ акции не может быть пустым. Пожалуйста, попробуйте снова.")

    for stock_symbol in stock_symbols:
        response = main_page(date_time_input, stock_symbol)
        print(response)


def handle_events_page():
    """Обрабатывает действия на странице событий и выводит информацию о расходах и доходах за определенный период."""
    print("Starting handle_events_page")
    date_time_input = input("Введите дату (YYYY-MM-DD HH:MM:SS): ")
    valid_date_time = validate_datetime(date_time_input)

    while not valid_date_time:
        print("Неверный формат даты. Попробуйте снова.")
        date_time_input = input("Введите дату (YYYY-MM-DD HH:MM:SS): ")
        valid_date_time = validate_datetime(date_time_input)

    period = input("Введите период (W, M, Y, ALL) или оставьте пустым для месячного периода: ").strip().upper() or "M"
    response = events_page(date_time_input, period)
    print(response)


if __name__ == "__main__":
    while True:
        page_type = input("Введите тип страницы (main/events) или 'exit' для выхода: ").strip().lower()
        if page_type == "exit":
            break
        elif page_type == "main":
            handle_main_page()
        elif page_type == "events":
            handle_events_page()
        else:
            print("Неверный ввод, попробуйте еще раз.")
