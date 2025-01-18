import random

from scripts.models.product import Product
from scripts.models.warehouse_on_db import Warehouse


def run():
    warehouse = Warehouse()
    # warehouse.db.create_product_type(Product(random.randint(1, 100000000), random.random(), random.random()))
    while True:
        request = warehouse.generate_new_request()
        print(request.get_data())


if __name__ == '__main__':
    run()
