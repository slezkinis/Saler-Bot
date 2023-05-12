import sqlite3


class SQL():
    def __init__(self) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS products(
        title TEXT,
        description TEXT,
        link TEXT,
        price INT,
        section TEXT,
        image TEXT);
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
        tgid INT,
        username TEXT,
        buyproducts TEXT);  
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS sections(
        title TEXT,
        id INT);
        """
        )
        # cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?);", ('Таблетка', 'Супер', 'https://yandex.ru', 199, 'Продукты', 'images/tabletka.jpg'))
        # conn.commit()
        # cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?);", ('Бот', 'Супер', 'https://google.com', 500, 'Продукты', 'images/Бот.jpg'))
        # conn.commit()
        # cur.execute("INSERT INTO sections VALUES(?, ?);", ('Продукты', 1))
        # conn.commit()
        # cur.execute("INSERT INTO users VALUES(?, ?, ?);", (1509726530, 'Ivan_Slezkin', ''))
        # conn.commit()
        conn.close()
    

    def get_info(self):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM products;")
        all_results = cur.fetchall()
        conn.close()
        return all_results

    def get_products_section(self, name):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM products where section='{name}';")
        all_results = cur.fetchall()
        conn.close()
        return all_results
    
    def get_info_about_product(self, text):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"select * from products where title='{text}'")
        product = cur.fetchone()
        return product

    def add_product(self, product):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?);", product)
        conn.commit()
        conn.close()

    def delete_product(self, title):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"DELETE from products where title = '{title}'")
        conn.commit()
        conn.close()

    def get_all_sections(self):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM sections;")
        all_results = cur.fetchall()
        conn.close()
        return all_results

    def create_section(self, name):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO sections VALUES(?, ?);", (name, 1))
        conn.commit()
        conn.close()

    def delete_section(self, name):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"DELETE from sections where title = '{name}'")
        conn.commit()
        conn.close()

    def get_all_users(self):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        all_results = cur.fetchall()
        conn.close()
        return all_results
    
    def get_user(self, tg_id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users where tgid={tg_id};")
        all_results = cur.fetchone()
        conn.close()
        return all_results

    def add_user(self, info):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES(?, ?, ?);", info)
        conn.commit()
        conn.close()

    def update_user(self, products, tg_id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(
        "UPDATE users SET buyproducts = ? WHERE tgid = ?",
        (products, tg_id)
        )
        conn.commit()
        conn.close()