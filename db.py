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
        conn.commit()
        cur.execute("""CREATE TABLE IF NOT EXISTS promocodes(
        id INT PRIMARY KEY,
        title TEXT,
        new_price INT);
        """
        )
        conn.commit()
        conn.close()
    
    # Products
    def get_all_products(self):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM products;")
        all_results = cur.fetchall()
        conn.close()
        return all_results

    def get_products_by_section(self, name):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM products where section={name};")
        all_results = cur.fetchall()
        conn.close()
        return all_results
    
    def get_product(self, id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"select * from products where id='{id}'")
        product = cur.fetchone()
        return product

    def create_product(self, product):
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

    # Sections
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
    
    # Users
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

    def update_user_buy(self, products, tg_id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(
        "UPDATE users SET buyproducts = ? WHERE tgid = ?",
        (products, tg_id)
        )
        conn.commit()
        conn.close()

    def update_user_money(self, tg_id, money):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET money = ? WHERE tgid = ?",
            (money, tg_id)
        )
        conn.commit()
        conn.close()
    
    # Promocodes
    def get_promocode(self, title):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM promocodes where title='{title}';")
        promocode = cur.fetchone()
        conn.close()
        return promocode

    def create_promocode(self, title, price):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM promocodes")
        id = len(cur.fetchall()) + 1
        cur = conn.cursor()
        cur.execute("INSERT INTO promocodes VALUES(?, ?, ?);", (id, title, price))
        conn.commit()
        conn.close()

    def get_all_promocodes(self):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM promocodes;")
        promocodes = cur.fetchall()
        conn.close()
        return promocodes

    def delete_promo(self, id):
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM promocodes WHERE id = {id};')
        promocode = cur.fetchone()[1]
        cur = conn.cursor()
        cur.execute(f"DELETE from promocodes where id = '{id}';")
        conn.commit()
        conn.close()
        return promocode
    