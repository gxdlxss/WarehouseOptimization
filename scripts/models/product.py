class Product(object):
    def __init__(self, sku: int, time_to_select: float, time_to_ship: float, **kwargs):
        self.sku = sku
        self.time_to_select = time_to_select
        self.time_to_ship = time_to_ship
        self.limits = dict(kwargs)

    def check_limits(self) -> None:
        pass

    def __str__(self):
        return str(self.sku)

    def __repr__(self):
        return self.__str__()
