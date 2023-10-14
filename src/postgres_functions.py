import psycopg2
from psycopg2 import sql



TABLE_NAME_CATEGORIES = 'categories'
TABLE_NAME_CATEGORY_LINKS = 'category_links'
TABLE_NAME_PRODUCT_CATEGORIES = 'product_categories'
TABLE_NAME_PRODUCTS = 'products'

# Общие функции postgresql

# Настройки по базе находятся в docker-compose
def db_connection():
    return psycopg2.connect(database="test_db_docker", user="admin", 
                            password="11111111", host="postgres", port="5432")


def check_table_exist(cur, table_name):
    # SQL-запрос для проверки существования таблицы
    cur.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")
    return cur.fetchone()[0]


def get_category_id(conn, category_name, tabel_name):
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM {tabel_name} WHERE category = '{category_name}';")
    category_id = cur.fetchone()

    if category_id:
        return category_id[0]
    else:
        return None
    

def create_tables_and_foreign_key(conn, main_table, table):
    cur = conn.cursor()
    
    if not check_table_exist(cur, table):
        # Создаем таблицу category_links
        cur.execute(f"CREATE TABLE {table} (id SERIAL PRIMARY KEY, category_id INT, data TEXT);")
        
        # Создаем внешний ключ, связывающий таблицу category_links с таблицей categories
        cur.execute(f"ALTER TABLE {table} ADD CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES {main_table}(id);")
    
    # Применяем изменения к базе данных
    conn.commit()


def create_data_category(conn, category, tabel_name):
    cur = conn.cursor()

    if not check_table_exist(cur, tabel_name):
        cur.execute(f"CREATE TABLE {tabel_name} (id SERIAL PRIMARY KEY, category TEXT UNIQUE);")
        cur.execute(f"ALTER TABLE {tabel_name} OWNER TO admin;")

    cur.execute(f"INSERT INTO {tabel_name} (category) VALUES ('{category}') ON CONFLICT (category) DO NOTHING;")

    # Записать в таблицу данные
    conn.commit()


# Функции для таблицы ссылок из общих категорий

def create_table_categories_data(conn, category_id, table_value, main_table, table):
    cur = conn.cursor()
    
    # Проверяем существование таблицы
    if not check_table_exist(cur, table):
        create_tables_and_foreign_key(conn, main_table, table)
        
    # Создаем внешний ключ, связывающий таблицу category_links с таблицей categories
    cur.execute(sql.SQL("INSERT INTO {} (category_id, {}) VALUES (%s, %s);").format(
        sql.Identifier(table),
        sql.Identifier("data")), (category_id, table_value))
    
    # Применяем изменения к базе данных
    conn.commit()