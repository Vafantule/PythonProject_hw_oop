class Product:
    """
    Класс, описывающий товар.
    """
    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name: str = name
        self.description: str = description
        self.price: float = price
        self.quantity: int = quantity


class Category:
    """
    Класс, описывающий категорию товаров.
    """
    category_count: int = 0
    product_count: int = 0

    def __init__(self, name: str, description: str, products: list):
        self.name: str = name
        self.description: str = description
        self.products: list[Product] = products

        Category.category_count += 1
        Category.product_count += len(products)
