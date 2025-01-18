import random

from scripts.models.interfaces.abstract_warehouse import AbstractWarehouse
from scripts.models.product import Product
from scripts.models.selection_request import SelectionRequest
from scripts.parsers.db_parser import Database


def Override(func):
    return func


class Warehouse(AbstractWarehouse):
    def __init__(self):
        self.db = Database()
        self.size = (0, 0)
        self.workers = 1

    def __get_cell(self, cell: tuple[int, int]):
        x, y = cell
        result = self.db.get_by_prompt(
            f'''
            SELECT id from Cell WHERE x={x}, y={y}
            '''
        )
        return result[0]

    def __get_all_from_cell(self, cell: tuple[int, int]) -> tuple:
        if not self.is_moving_cell(cell):
            result = self.db.get_by_prompt(
                f'''
                SELECT * from Warehouse WHERE cell_id={self.__get_cell(cell)}
                '''
            )
            return result
        return None

    def __get_all_from_cell_as_set(self, cell: tuple[int, int]) -> set:
        result = set()
        for product_id in self.__get_all_from_cell(cell):
            sku, count = self.db.get_by_prompt(
                f'''
                SELECT (sku, count) from Warehouse WHERE id={product_id}
                '''
            )
            product = self.db.get_by_prompt(
                f'''
                SELECT * from Products WHERE sku={sku}
                '''
            )
            product = Product(*product)
            result[product] = result.get(product, 0) + count
        return result

    @Override
    def get_type_of_product_on_cell(self, cell: tuple[int, int]) -> Product:
        result = self.__get_all_from_cell(cell)
        sku = result[1]
        product = self.db.get_by_prompt(
                f'''
                SELECT * from Products WHERE sku={sku}
                '''
            )[0]
        return Product(*product)

    @Override
    def check_type_of_product_on_cell(self, cell: tuple[int, int], product: Product) -> bool:
        return product.sku == self.get_type_of_product_on_cell(cell).sku

    @Override
    def is_moving_cell(self, cell: tuple[int, int]) -> bool:
        x, y = cell
        result = self.db.get_by_prompt(
            f'''
            SELECT * from Cells WHERE x={x}, y={y}
            '''
        )
        return len(result)

    @Override
    def remove_product_from_cell(self, count: int, cell: tuple[int, int]) -> None:
        cell_id = self.__get_cell(cell)
        cur_products = self.__get_all_from_cell_as_set(cell)
        self.db.execute(
            f'''
            DELETE FROM Warehouse WHERE cell_id={cell_id}
            '''
        )
        for product in cur_products:
            cur_products[product] -= count
            self.db.execute(
                '''
                INSERT INTO Warehouse (sku, count, cell_id) VALUES (?, ?, ?)
                ''',
                params=(product.sku, cur_products[product], cell_id)
            )

    @Override
    def add_product_to_cell(self, count: int, cell: tuple[int, int], product=None) -> None:
        cell_id = self.__get_cell(cell)
        cur_products = self.__get_all_from_cell_as_set(cell)
        self.db.execute(
            f'''
            DELETE FROM Warehouse WHERE cell_id={cell_id}
            '''
        )
        cur_products[product] = cur_products.get(product, 0)
        cur_products[product] += count
        self.db.execute(
            '''
            INSERT INTO Warehouse (sku, count, cell_id) VALUES (?, ?, ?)
            ''',
            params=(product.sku, cur_products[product], cell_id)
        )

    @Override
    def add_workers(self, count: int) -> int:
        self.workers += count
        return self.workers

    @Override
    def remove_workers(self, count: int) -> int:
        self.workers -= count
        return self.workers

    @Override
    def generate_new_request(self) -> SelectionRequest:
        products = self.db.get_all_products()
        products = [Product(*p) for p in products]
        size = random.randint(1, max(1, len(products) // 2))
        result = list()
        for _ in range(size):
            product = random.choice(products)
            products.remove(product)
            result.append((product, random.randint(1, 10)))
        return SelectionRequest(*result)

    @Override
    def fill(self) -> None:
        cells = self.db.get_all_cells()
        products = self.db.get_all_products()
        products = [p[0] for p in products]
        for cell in cells:
            if 0.5 >= random.random():
                product = random.choice(products)
                self.db.execute(
                    '''
                    INSERT INTO Warehouse (sku, count, cell_id) VALUES (?, ?, ?)
                    ''',
                    params=(product, 64, cell)
                )

    @Override
    def build(self, layout) -> None:
        self.db.execute(
            '''
            DELETE * FROM Warehouse
            '''
        )
        self.db.execute(
            '''
            DELETE * FROM Cells
            '''
        )
        self.size = (len(layout), len(layout[0]))
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if layout[x][y]:
                    self.db.cursor.execute(
                        '''
                        INSERT INTO Cells (x, y) VALUES (?, ?)
                        ''',
                        (x, y)
                    )
        self.db.connection.commit()
        self.fill()
