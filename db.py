import sqlite3


class SQL():
    def __init__(self) -> None:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS products(
        id INT PRIMARY KEY,
        title TEXT,
        description TEXT,
        link TEXT,
        old_price INT,
        new_price INT,
        section INT,
        image TEXT);
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
        tgid INT,
        username TEXT,
        buyproducts TEXT,
        money INT,
        ref INT);
        """)
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS sections(
        title TEXT,
        id INT PRIMARY KEY);
        """
        )
        # cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?, ?);", (1, 'Таблетка', 'Супер', 'https://yandex.ru', 199, 1, 'images/tabletka.jpg'))
        # conn.commit()
        # cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?, ?);", (2, 'Бот', 'Супер', 'https://google.com', 500, 1, 'images/Бот.jpg'))
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
        # print(all_results)
        return all_results

    def get_products_section(self, name):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM products where section={name};")
        all_results = cur.fetchall()
        conn.close()
        return all_results
    
    def get_info_about_product(self, id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"select * from products where id='{id}'")
        product = cur.fetchone()
        return product

    def add_product(self, product):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        id = len(cur.fetchall()) + 1
        cur = conn.cursor()
        otv = [id]
        for i in product:
            otv.append(i)
        cur.execute("INSERT INTO products VALUES(?, ?, ?, ?, ?, ?, ?, ?);", otv)
        conn.commit()
        conn.close()

    def delete_product(self, id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"DELETE from products where id = '{id}'")
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
        cur.execute("SELECT * FROM sections")
        id = len(cur.fetchall()) + 1
        cur = conn.cursor()
        cur.execute("INSERT INTO sections VALUES(?, ?);", (name, id))
        conn.commit()
        conn.close()

    def get_section(self, id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM sections where id = {id}")
        return cur.fetchone()

    def delete_section(self, id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"DELETE from sections where id = '{id}'")
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
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?);", info)
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