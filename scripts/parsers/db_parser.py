import sqlite3 as sql

from scripts.models.product import Product


class Database(object):
    def __init__(self):
        self.connection = sql.connect('db/db.db')
        self.cursor = self.connection.cursor()
        self.init_tables()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def execute(self, prompt: str, params=()) -> None:
        self.cursor.execute(prompt, params)
        self.__commit()

    def get_by_prompt(self, prompt: str) -> tuple:
        return self.cursor.execute(prompt).fetchall()

    def init_tables(self) -> None:
        self.execute(
            '''
            CREATE TABLE IF NOT EXISTS Cells (
            id INTEGER PRIMARY KEY,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL
            )
            '''
        )
        self.execute(
            '''
            CREATE TABLE IF NOT EXISTS Products (
            sku INTEGER PRIMARY KEY,
            time_to_select REAL NOT NULL,
            time_to_ship REAL NOT NULL
            )
            '''
        )
        self.execute(
            '''
            CREATE TABLE IF NOT EXISTS Warehouse (
            id INTEGER PRIMARY KEY,
            sku INTEGER NOT NULL,
            count INTEGER NOT NULL,
            cell_id INTEGER NOT NULL,
            FOREIGN KEY (sku) REFERENCES Products (sku),
            FOREIGN KEY (cell_id) REFERENCES Cells (id)
            )
            '''
        )

    def __commit(self):
        self.connection.commit()

    def create_product_type(self, product: Product) -> None:
        self.execute(
            '''
            INSERT INTO Products (sku, time_to_select, time_to_ship) VALUES (?, ?, ?)
            ''',
            params=(product.sku, product.time_to_select, product.time_to_ship)
        )
