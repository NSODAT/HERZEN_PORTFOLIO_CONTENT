import json
import sqlite3
import datetime

def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(s):
    return datetime.fromisoformat(s)

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

def logger(handle=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if handle is None:
                print(f'Function {func.__name__} called with args: {args}, kwargs: {kwargs} and returned {result}')
            elif isinstance(handle, str):
                with open(handle, 'a') as f:
                    record = {
                        'datetime': datetime.datetime.now().isoformat(),
                        'func_name': func.__name__,
                        'params': list(args) + list(kwargs.values()),
                        'result': result
                    }
                    json.dump(record, f)
                    f.write('\n')
            elif isinstance(handle, sqlite3.Connection):
                # Register the custom datetime adapter
                sqlite3.register_adapter(datetime.datetime, adapt_datetime)
                sqlite3.register_converter("timestamp", convert_datetime)

                cursor = handle.cursor()
                cursor.execute("INSERT INTO logs (datetime, func_name, params, result) VALUES (?, ?, ?, ?)",
                               (datetime.datetime.now(), func.__name__, json.dumps(list(args) + list(kwargs.values())), result))
                handle.commit()

            return result
        return wrapper
    return decorator

def print_logs(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")

        for row in cursor.fetchall():
            print(f'{row[0]}: {row[1]}({row[2]}) = {row[3]}')

        conn.close()
    except sqlite3.DatabaseError as e:
        print(f"Ошибка подключения к базе данных: {e}")

def main():
    # Запросить у пользователя тип вывода результата работы функций
    output_type = input("Введите тип вывода результата работы функций (stdout, json, sqlite): ")

    # Создать дескриптор в зависимости от указанного пользователем типа вывода
    if output_type == "stdout":
        handle = None
    elif output_type == "json":
        handle = 'logs.json'
    elif output_type == "sqlite":
        try:
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, datetime TEXT, func_name TEXT, params TEXT, result TEXT)")
            conn.commit()
            handle = conn
        except sqlite3.DatabaseError as e:
            print(f"Ошибка создания базы данных SQLite: {e}")
    else:
        raise ValueError("Неверный тип вывода")

    # Использовать декоратор logger с указанным дескриптором
    @logger(handle=handle)
    def sum_nums(nums):
        return sum(nums)

    @logger(handle=handle)
    def process_string(string):
        return string.upper()

    @logger(handle=handle)
    def analyze_collection(collection):
        return max(collection)

    # Вызвать функции и вывести результаты
    print(sum_nums((1, 2, 3)))
    print(process_string('Hello'))
    print(analyze_collection([1, 2, 3]))

    # Вывести данные из базы данных SQLite на экран
    if output_type == "sqlite":
        print_logs('logs.json')

if __name__ == "__main__":
    main()