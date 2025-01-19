from scripts.models.selection_request import SelectionRequest


class Graph:
    def __init__(self, wh):
        self.wh = wh
        self.matrix = list()
        self.build()

    def build(self):
        pass

    def solve(self, request: SelectionRequest) -> list:
        result = list()
        for pair in request.get_data():
            product, count = pair
            while count > 0:
                points = self.wh.db.get_by_prompt(f'SELECT * FROM Warehouse WHERE sku={product.sku}')
                if not points:
                    self.wh.fill()
                    return None
                for point in points:
                    cell = self.wh.db.get_by_prompt(f'SELECT x, y FROM Cells WHERE id={point[3]}')[0]
                    result.append(cell)
                    if point[2] < count:
                        count -= point[2]
                        self.wh.db.execute(f'DELETE FROM Warehouse WHERE id={point[0]}')
                    else:
                        self.wh.remove_product_from_cell(count, cell)
                        count = 0
                        break
        return result
