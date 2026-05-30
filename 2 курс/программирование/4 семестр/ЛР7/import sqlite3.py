import sqlite3
from datetime import datetime


class Counter:
    def __init__(self, value=0):
        self.value = value

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1

    def reset(self):
        self.value = 0


def with_connection(db_path):
    def with_connection_decorator(func):
        def func_wrapper(*args, **kwargs):
            with sqlite3.connect(db_path) as conn:
                return func(conn, *args, **kwargs)
        return func_wrapper
    return with_connection_decorator


@with_connection("data.sqlite3")
def db_table_create(conn, create_table_sql):
    cur = conn.cursor()
    cur.execute(create_table_sql)
    conn.commit()


@with_connection("data.sqlite3")
def create_data(conn, counter):
    cur = conn.cursor()
    cur.execute("INSERT INTO counter (value, created) VALUES (:value, :created)",
                {"value": counter.value, "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    conn.commit()


@with_connection("data.sqlite3")
def search_data(conn, search_params):
    cur = conn.cursor()
    # Подготовка запроса с использованием параметров поиска
    query = "SELECT * FROM counter WHERE "
    query_conditions = []
    params = {}
    if search_params['id']:
        query_conditions.append("id = :id")
        params['id'] = search_params['id']
    if search_params['value']:
        query_conditions.append("value = :value")
        params['value'] = search_params['value']
    if search_params['created']:
        query_conditions.append("strftime('%Y-%m-%d', created) = :created")
        params['created'] = search_params['created']
    query += " AND ".join(query_conditions)
    
    # Логирование запроса
    print(f"Выполняемый запрос: {query}")
    print(f"С параметрами: {params}")
    
    cur.execute(query, params)
    row = cur.fetchone()
    if row:
        return row
    else:
        return "строка не найдена!"
    

@with_connection("data.sqlite3")
def read_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM counter")
    rows = cur.fetchall()
    for row in rows:
        print(row)


@with_connection("data.sqlite3")
def update_data(conn, id, counter):
    cur = conn.cursor()
    cur.execute("UPDATE counter SET value = :value WHERE id = :id",
                {"id": id, "value": counter.value})
    conn.commit()


@with_connection("data.sqlite3")
def delete_data(conn, id):
    cur = conn.cursor()
    cur.execute("DELETE FROM counter WHERE id = :id", {"id": id})
    conn.commit()


def user_input():
    id = int(input("Введите id: "))
    value = int(input("Введите значение: "))
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {"id": id, "value": value, "created": created}


def get_params_for_search():
    params = {}
    params['id'] = input("Введите id для поиска: ")
    params['value'] = input("Введите значение для поиска: ")
    params['created'] = input("Введите дату создания для поиска (YYYY-MM-DD): ")
    return params


def main():
    create_table_sql = """CREATE TABLE IF NOT EXISTS counter (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        value INT,
                        created DATETIME);"""
    
    db_table_create(create_table_sql)
    
    user_data = user_input()
    
    counter = Counter(value=user_data['value'])
    
    create_data(counter)
    
    read_data()
    
    counter.increment()
    update_data(user_data['id'], counter)
    
    delete_data(user_data['id'])
    

    read_data()
    search_params = get_params_for_search()
    
    # Здесь функционал для поиска данных в БД с использованием search_params

    search_result = search_data(search_params)
    if isinstance(search_result, tuple):
        print(f"Найденная строка: {search_result}")
    else:
        print(search_result)


if __name__ == "__main__":
    main()