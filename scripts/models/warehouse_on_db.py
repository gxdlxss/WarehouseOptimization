import random
from collections.abc import Mapping
from typing import Optional, override

from scripts.exceptions.warehouse_exceptions import FireTooManyWorkersException, EmptyCellException, WarehouseException
from scripts.models.interfaces.abstract_warehouse import AbstractWarehouse
from scripts.models.product import Product
from scripts.models.selection_request import SelectionRequest
from scripts.parsers.db_parser import Database


class Warehouse(AbstractWarehouse):
    def __init__(self):
        self.db = Database()
        self.size = (0, 0)
        self.PROBABILITY_OF_FILLING_CELL = 0.33
        self.MAX_COUNT_TO_ADD_ON_EMPTY_CELL = 64
        self.MAX_COUNT_TO_ADD_ON_NOT_EMPTY_CELL = 16
        self.workers = 1

    def __get_cell(self, cell: tuple[int, int]) -> Optional[int]:
        x, y = cell
        result = self.db.get_by_prompt(
            f'''
            SELECT id FROM Cells WHERE x={x} AND y={y}
            '''
        )
        return result[0][0] if result else None

    def __get_all_from_cell(self, cell: tuple[int, int]) -> Optional[tuple]:
        result = self.db.get_by_prompt(
            f'''
            SELECT * FROM Warehouse WHERE cell_id={self.__get_cell(cell)}
            '''
        )
        return result[0][0] if result else None

    def __get_all_from_cell_as_set(self, cell: tuple[int, int]) -> set:
        result = set()
        product = self.__get_all_from_cell(cell)

        if product:
            _, sku, count, __ = product

            product = self.db.get_by_prompt(
                f'''
                SELECT * FROM Products WHERE sku={sku}
                '''
            )
            product = Product(*product)

            result[product] = result.get(product, 0) + count
        return result

    @override
    def get_type_of_product_on_cell(self, cell: tuple[int, int]) -> Product:
        result = self.__get_all_from_cell(cell)

        if not result:
            raise EmptyCellException("На данной ячейке ничего не лежит")

        sku = result[1]
        product = self.db.get_by_prompt(
                f'''
                SELECT * FROM Products WHERE sku={sku}
                '''
            )[0]
        return Product(*product)

    @override
    def check_type_of_product_on_cell(self, cell: tuple[int, int], product: Product) -> bool:
        return product.sku == self.get_type_of_product_on_cell(cell).sku

    @override
    def is_moving_cell(self, cell: tuple[int, int]) -> bool:
        x, y = cell
        if x > max(self.size) or y > max(self.size):
            return True

        result = self.__get_cell(cell)
        return not result

    @override
    def remove_product_from_cell(self, count: int, cell: tuple[int, int]) -> None:
        cell_id = self.__get_cell(cell)
        cur_products = self.__get_all_from_cell_as_set(cell)

        self.db.execute(
            f'''
            DELETE FROM Warehouse WHERE cell_id={cell_id}
            '''
        )

        for product in cur_products:
            if cur_products[product] - count >= 0:
                cur_products[product] -= count
            if cur_products[count] > 0:
                self.db.execute(
                    '''
                    INSERT INTO Warehouse (sku, count, cell_id) VALUES (?, ?, ?)
                    ''',
                    params=(product.sku, cur_products[product], cell_id)
                )

    @override
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

    @override
    def add_workers(self, count: int) -> int:
        self.workers += count
        return self.workers

    @override
    def remove_workers(self, count: int) -> int:
        if self.workers - count < 0:
            raise FireTooManyWorkersException("Нельзя распустить больше работников, чем имеется")

        self.workers -= count
        return self.workers

    @override
    def generate_new_request(self) -> SelectionRequest:
        products = self.db.get_all_products()
        if not products:
            raise EmptyListOfProductsException("В базе данных нет ни одного продукта для создания запроса")

        products = [Product(*p) for p in products]
        size = random.randint(1, max(1, len(products) // 2))
        result = list()

        for _ in range(size):
            product = random.choice(products)
            products.remove(product)
            result.append((product, random.randint(1, 10)))

        return SelectionRequest(*result)

    @override
    def fill(self) -> None:
        cells = self.db.get_all_cells()
        if not all(self.size) or not cells:
            raise EmptyCellException("На складе нет ни одной ячейки")

        products = self.db.get_all_products()
        products = [p[0] for p in products]

        for cell in cells:
            cell_id, x, y = cell

            if self.PROBABILITY_OF_FILLING_CELL >= random.random():
                if self.is_empty_cell((x, y)):
                    product_sku = random.choice(products)
                    count = random.randint(1, self.MAX_COUNT_TO_ADD_ON_EMPTY_CELL)
                else:
                    product_sku = self.get_type_of_product_on_cell((x, y))
                    count = random.randint(1, self.MAX_COUNT_TO_ADD_ON_NOT_EMPTY_CELL)

                self.db.execute(
                    '''
                    INSERT INTO Warehouse (sku, count, cell_id) VALUES (?, ?, ?)
                    ''',
                    params=(product_sku, count, cell_id)
                )

    @override
    def build(self, layout) -> None:
        if not len(layout) or not len(layout[0]):
            raise IllegalSizeException("Нельзя создать склад с нулём ячеек")
        self.size = (len(layout), len(layout[0]))

        self.db.execute(
            '''
            DELETE FROM Warehouse
            '''
        )
        self.db.execute(
            '''
            DELETE FROM Cells
            '''
        )

        for x in range(self.size[0]):
            if len(layout[x]) != self.size[1]:
                raise IncompleteMapException("Переданная карта ячеек имеет непрямоугольный размер")

            for y in range(self.size[1]):
                if layout[x][y]:
                    self.db.cursor.execute(
                        '''
                        INSERT INTO Cells (x, y) VALUES (?, ?)
                        ''',
                        (x, y)
                    )
        self.db.connection.commit()

        try:
            self.fill()
        except WarehouseException:
            pass

    @override
    def is_empty_cell(self, cell: tuple[int, int]) -> bool:
        cell_id = self.__get_cell(cell)
        connections_with_cell = self.db.get_by_prompt(
            f'''
            SELECT * FROM Warehouse WHERE cell_id={cell_id}
            '''
        )
        return not connections_with_cell

    @override
    def solve(self, request: SelectionRequest) -> Optional[dict]:  # todo on C++
        pass
