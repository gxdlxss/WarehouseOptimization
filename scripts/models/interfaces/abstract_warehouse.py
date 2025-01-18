from typing import Optional

from scripts.models.product import Product
from scripts.models.selection_request import SelectionRequest


class AbstractWarehouse(object):
    size: tuple[int, int]

    def get_type_of_product_on_cell(self, cell: tuple[int, int]) -> Product:
        pass

    def check_type_of_product_on_cell(self, cell: tuple[int, int], product: Product) -> bool:
        pass

    def is_moving_cell(self, cell: tuple[int, int]) -> bool:
        pass

    def remove_product_from_cell(self, count: int, cell: tuple[int, int]) -> None:
        pass

    def add_product_to_cell(self, count: int, cell: tuple[int, int], product=None) -> None:
        pass

    def add_workers(self, count: int) -> int:
        pass

    def add_worker(self) -> int:
        return self.add_workers(1)

    def remove_workers(self, count: int) -> int:
        pass

    def remove_worker(self) -> int:
        return self.remove_workers(1)

    def generate_new_request(self) -> SelectionRequest:
        pass

    def fill(self) -> None:
        pass

    def build(self, layout) -> None:
        pass

    def is_empty_cell(self, cell: tuple[int, int]) -> bool:
        pass

    def solve(self, request: SelectionRequest) -> Optional[list]:
        pass
