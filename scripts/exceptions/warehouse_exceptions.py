class WarehouseException(Exception):
    pass


class EmptyCellException(WarehouseException):
    pass


class FireTooManyWorkersException(WarehouseException):
    pass


class EmptyListOfProductsException(WarehouseException):
    pass


class BuildException(WarehouseException):
    pass


class IllegalSizeException(BuildException):
    pass


class IncompleteMapException(BuildException):
    pass
