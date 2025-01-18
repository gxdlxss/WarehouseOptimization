import json
from typing import Optional

from scripts.exceptions.json_parser_exceptions import ExecutionError
from scripts.models.warehouse_on_db import Warehouse


class ParserManager(object):
    def __init__(self):
        self.warehouse = Warehouse()
        self.namespase = {
            "solve": solve,
            "warehouse_map": build_map,
            "answer": do_nothing,
            "update_map": do_nothing
        }

    def __call__(self, *args, **kwargs):
        args = list(args)
        if not args or args[0] in self.namespase:
            item = args[0]
            args[0] = self.warehouse
            return self.namespase[item](*args, **kwargs)
        else:
            raise KeyError("Неизвестный протокол обмена")

    def __getitem__(self, item: str):
        if item in self.namespase:
            return self.namespase[item]
        else:
            raise KeyError("Неизвестный протокол обмена")

    def execute(self, data: dict) -> None:
        if not isinstance(data, dict) or 'type' not in data:
            raise ExecutionError("Ошибка обработки команды")
        return self(data['type'], data)


async def do_nothing(*args, **kwargs) -> None:
    pass


async def build_map(warehouse: Warehouse, data: dict) -> None:
    warehouse.build(data["map"])


async def solve(warehouse: Warehouse) -> Optional[dict]:
    return warehouse.solve(warehouse.generate_new_request())
