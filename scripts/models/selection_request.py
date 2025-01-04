from scripts.models.product import Product


class SelectionRequest(object):
    def __init__(self, *args):
        self.data = dict()
        self.add_products_from_list(args)

    def add_products_from_list(self, products: Iterable) -> None:
        for element in products:
            if not isinstance(element, tuple):
                raise Exception()
            if len(element) != 2:
                raise Exception()
            if not isinstance(element[0], Product):
                raise Exception()
            if not isinstance(element[1], int):
                raise Exception()

            product, count = element
            self.data[product] = self.data.setdefault(product, 0) + count
